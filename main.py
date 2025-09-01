
import streamlit as st
import pandas as pd
import re
import io

def clean_text(text, fill_value):
    if pd.isna(text) or str(text).strip() == '':
        return fill_value

    text = str(text).strip()
    try:
        text = text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    text=re.sub(r'[+$₹#]','',text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[\r\n]+', ' ', text)
    text = text.replace('\\r', ' ').replace('\\n', ' ')
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def clean_dataframe(df, fill_value):
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
    for col in df.columns:
        df[col] = df[col].map(lambda x: clean_text(x, fill_value))
    return df

def download_file(df, output_name, output_format):
    towrite = io.BytesIO()

    if output_format == 'Excel':
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_ext = '.xlsx'

    elif output_format == 'CSV':
        df.to_csv(towrite, index=False)
        mime = 'text/csv'
        file_ext = '.csv'


    elif output_format == 'JSON':
        string_io = io.StringIO()
        df.to_json(string_io, orient='records', lines=True)
        towrite = string_io.getvalue().encode()
        mime = 'application/json'
        file_ext = '.json'

    else:
        return

    towrite.seek(0)
    st.download_button(
        label="📥 Download Cleaned File",
        data=towrite,
        file_name=f"{output_name}{file_ext}",
        mime=mime
    )

st.title("🧼 Data Cleaner ")

st.header("Upload Excel or CSV to Clean")

fill_choice = st.radio("Fill empty values with:", ["N/A", "Blank"])
fill_value = "N/A" if fill_choice == "N/A" else ""

uploaded_file = st.file_uploader("Choose Excel or CSV file", type=["xlsx", "xls", "csv"])
output_name = st.text_input("Output file name", value="cleaned_file")
output_format = st.selectbox("Download format", ["Excel", "CSV", "JSON"])

if uploaded_file:
    try:
        ext = uploaded_file.name.split('.')[-1].lower()

        if ext in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        elif ext == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(uploaded_file, encoding='latin1')
        else:
            st.error("Unsupported file format.")
            st.stop()

        df = clean_dataframe(df, fill_value)
        st.success("✅ File cleaned successfully!")
        st.dataframe(df.head())

        download_file(df, output_name, output_format)

    except Exception as e:
        st.error(f"Error: {e}")
