import streamlit_authenticator as stauth

hashed_pw = stauth.Hasher(passwords=['techxos123']).generate()
print(hashed_pw)
