import pandas as pd

def validate_user(email:str, password:str, user_df:pd.DataFrame) -> bool:

    if user_df.empty:
        return False
    
    user = user_df[user_df['email'].str.lower() == email.lower()]
    return not user.empty and user.iloc[0]['senha'] == password

def validate_user_data(user_df:pd.DataFrame):
    required_columns = ['email', 'senha']
    for col in required_columns:
        if col not in user_df.columns:
            raise ValueError(f"Missing required colum: {col}")
    
    user_df['senha'] = user_df['senha'].astype(str)