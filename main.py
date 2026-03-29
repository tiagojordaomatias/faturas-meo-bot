import os
import imaplib
import email
from email.header import decode_header
import fitz

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]

NOME_PARTES = ["tiago", "matias"]
NIF = "231275900"

def extrair_texto_pdf(caminho):
    texto = ""
    doc = fitz.open(caminho)
    for page in doc:
        texto += page.get_text()
    return texto.lower()

def contem_dados(texto):
    texto_sem_espacos = texto.replace(" ", "").replace("\n", "")
    nif_ok = NIF in texto_sem_espacos
    nome_ok = all(p in texto for p in NOME_PARTES)
    return nif_ok or nome_ok

def main():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, 'FROM', '"meo"')
    messages = messages[0].split()

    os.makedirs("faturas", exist_ok=True)

    for num in messages:
        status, data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename and filename.lower().endswith(".pdf"):

                filepath = f"faturas/{filename}"

                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))

                texto = extrair_texto_pdf(filepath)

                if contem_dados(texto):
                    print(f"OK: {filename}")
                else:
                    os.remove(filepath)

if __name__ == "__main__":
    main()
