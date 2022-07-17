

""" user = "nlp_testmail@libero.it"
password = "FrancoCutugno95!" """

# %%
#import the smtplib library
import smtplib

# creating SMTP server
server = smtplib.SMTP_SSL('smtp.libero.it ', 465)

# %% start server and use TLS for security
server.ehlo()
server.starttls()


# %% write a message
oggetto = "Subject: Urgente! da leggere subito!\n\n"
contenuto = "dobbiamo finire NLP"
message = oggetto + contenuto

# for Authentication
server.login("nlp_testmail@libero.it", "FrancoCutugno95!")


# %% sending the email
server.login("nlp_testmail@libero.it", "FrancoCutugno95!")
server.sendmail("nlp_testmail@libero.it", "fulvio.camera95@hotmail.com", message)

print("Successfully sent email")
# terminate the session
server.quit