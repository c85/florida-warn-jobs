FROM python:3.10
COPY . /usr/app/
WORKDIR /usr/app/
RUN pip install -r requirements.txt
CMD streamlit run main.py --server.port 80