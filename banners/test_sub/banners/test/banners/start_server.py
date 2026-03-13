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
import paramiko, os, time, rpyc

def logM(message):
    file = open(os.path.dirname(os.path.realpath(__file__)) + '/utils/logs', 'a')
    # file = open('/var/www/html/ii_module1/utils/logs', 'a')
    file.write('\n' + time.strftime('%Y-%m-%d_%H:%M:%S') + '\n' + message + '\n')
    file.close()

class Work():
    # model = 'gemma3:12b'
    model = 'gemma3:27b'
    llm = OllamaLLM(model=model)
    embeddings = OllamaEmbeddings(model='bge-m3')
    loader = CSVLoader(file_path='/home/gen/subcategory_new.csv')
    pages = loader.load_and_split()
    store = DocArrayInMemorySearch.from_documents(pages, embedding=embeddings)
    retriever = store.as_retriever()
    # У тебя есть список кортежей, в которых есть соответствие ID и названия категории. Выбери наиболее подходящую по смыслу категорию и верни соответствующий кортеж. Делай выбор в любом случае, отвечай кортежем, который наиболее подходит. Также оцени от 0 до 100 процент уверенности в своем выборе.
    template = """
    У тебя есть список кортежей, в которых есть соответствие ID и названия категории. Выбери наиболее подходящую по смыслу категорию и верни соответствующее ей ID. Делай выбор в любом случае. Также оцени от 0 до 100 процент уверенности в своем выборе, отвечая только числом, без пояснений. Ответь в формате ID§Процент уверенности

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
        logM('failed connect to old server')
    def get_brand_and_category_id(self, img_path, ad_link):
        # response: ChatResponse = chat(model=self.model, messages=[ { 'role': 'user', 'content': 'Предложи несколько вариантов категорий, к которым ты бы отнес рекламируемый на картинке продукт, используя не более 10 слов. Отвечай на русском языке', 'images': [img_path]}, ])
        response: ChatResponse = chat(model=self.model, messages=[ { 'role': 'user', 'content': 'Укажи бренд, который рекламируется на вложенной картинке. Учитывай название ссылки, на которую ведет данная картинка: ' + ad_link + ' Ссылка может содержать название бренда. Используй текст ссылки в том случае, если однозначно определить бренд на картинке не удалось. Ответь исключительно названием бренда, не дописывай ничего от себя и не ставь никаких дополнительных символов. Также предложи наиболее подходящую по твоему мнению категорию, к которой ты бы отнес рекламируемый на картинке продукт, используя не более 10 слов. Если ты не уверен, предложи несколько категорий через точку с запятой. Отвечай на русском языке. Ответь в формате "Название бренда"§"Слова"', 'images': [img_path]}, ])
        answer = response['message']['content']
        brand = 'null'
        category_id = 0
        percentage = 0
        if '§' in answer:
            arr = answer.split('§')
            brand = arr[0]
            words = arr[1]
            arr = self.chain.invoke(words)
            if '§' in arr:
                arr = arr.split('§')
                category_id = arr[0]
                percentage = (arr[1]).strip()
                logM('banner: ' + img_path + ', words: ' + words + ', category id: ' + str(category_id) + ', percentage: ' + str(percentage) + ', brand: ' + brand)
        return brand + '§' + category_id + '§' + percentage
    def pass_data_to_old_server(self, data_json):
        if self.old_server_is_ok == False:
            return ['Ошибка подключения к старому серверу']
        stdin, stdout, stderr = self.ssh.exec_command("python3.10 /var/www/html/ii_module1/data_to_db.py '" + data_json + "'")
        return stderr.readlines()
    def ask_ai(self, message):
        if message != '':
            response: ChatResponse = chat(model=self.model, messages=[ { 'role': 'user', 'content': message} ])
            return response['message']['content']
    def ask_ai_img(self, message, img_path):
        if message != '':
            response: ChatResponse = chat(model=self.model, messages=[ { 'role': 'user', 'content': message, 'images': [img_path]} ])
            return response['message']['content']

class MyService(rpyc.Service):
    def exposed_get_brand_and_category_id(self, img_path, ad_link):
        return main.get_brand_and_category_id(img_path, ad_link)
    def exposed_pass_data_to_old_server(self, data_json):
        return main.pass_data_to_old_server(data_json)
    def exposed_ask_ai(self, message):
        return main.ask_ai(message)
    def exposed_ask_ai_img(self, message, img_path):
        return main.ask_ai_img(message, img_path)

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
