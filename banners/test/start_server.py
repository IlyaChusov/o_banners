# SERVER app 04
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_ollama import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sys import argv
from langchain_ollama import OllamaLLM
from ollama import ChatResponse
from ollama import chat
import paramiko

class Work():
    # model = 'gemma3:12b'
    model = 'gemma3:27b'
    llm = OllamaLLM(model=model)
    embeddings = OllamaEmbeddings(model='bge-m3')
    loader = CSVLoader( file_path="/home/gen/subcats_only.csv", csv_args={ "delimiter": "§", "quotechar": '"', }, )
    pages = loader.load_and_split()
    store = DocArrayInMemorySearch.from_documents(pages, embedding=embeddings)
    retriever = store.as_retriever()
    template = """
    Отвечай на вопросы, исходя из содержания документа.
    Документ содержит категории. Я буду вводить слова, к которым ты должен подобрать наиболее подходящую категорию.
    Отвечай только названием категории.

    Контекст: {context}

    Вопрос: {question}
    """
    prompt = PromptTemplate.from_template(template)
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    chain = (
    {
        'context': retriever | format_docs,
        'question': RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
    )
    # Для передачи данных старому серверу
    old_server_is_ok = False
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.connect('cs3-app-01.advmoscow.ru', 22, 'IChusov', 'U&!t#J7P7P7kn')
        old_server_is_ok = True
    except Exception as C:
        print('failed connect to old server')
    def get_brand(self, img_path):
        response: ChatResponse = chat(model=self.model, messages=[ { 'role': 'user', 'content': 'Укажи бренд, который рекламируется на вложенной картинке. Ответь одним словом', 'images': [img_path]}, ])
        return response['message']['content']
    def get_category(self, img_path):
        response: ChatResponse = chat(model=self.model, messages=[ { 'role': 'user', 'content': 'Предложи несколько вариантов категорий, к которым ты бы отнес рекламируемый на картинке продукт, используя не более 10 слов. Отвечай на русском языке', 'images': [img_path]}, ])
        words = response['message']['content']
        return self.chain.invoke(words)
    def pass_data_to_old_server(self, data_json):
        if self.old_server_is_ok == False:
            return ['Ошибка подключения к старому серверу']
        stdin, stdout, stderr = self.ssh.exec_command("python3.10 /var/www/html/ii_module1/data_to_db.py '" + data_json + "'")
        return stderr.readlines()

# rpyc servic definition
import rpyc

class MyService(rpyc.Service):
    def exposed_get_brand(self, img_path):
        return main.get_brand(img_path)
    def exposed_get_category(self, img_path):
        return main.get_category(img_path)
    def exposed_pass_data_to_old_server(self, data_json):
        return main.pass_data_to_old_server(data_json)

# start the rpyc server
from rpyc.utils.server import ThreadedServer
from threading import Thread
server = ThreadedServer(MyService, port = 12345)
t = Thread(target = server.start)
t.daemon = True
t.start()

# the main logic
main = Work()

while True:
    pass

