import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from textblob import TextBlob
# from langchain.memory.chat_message_histories import ChatMessageHistory 


from dotenv import load_dotenv
import json
from channels.generic.websocket import AsyncWebsocketConsumer

#loading env variables
load_dotenv()
os.environ["LANGCHAIN_API_KEY"]= os.getenv("LANGCHAIN_API_KEY")
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"

#initialize llm model
llm=ChatOpenAI(model_name="gpt-3.5-turbo")
outputparser=StrOutputParser()
prompt=ChatPromptTemplate.from_template("You are a helpful assistant. Respond to: {message}")

# memory buffer
memory=ConversationBufferMemory(memory_key='history')


class TestWebSocket(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name='test'

        await self.channel_layer.group_add(
             self.room_group_name,
             self.channel_name
        )
        await self.accept()


    async def disconnect(self,close_code):
            print("Websocket disconnect")

    async def receive(self,text_data):
        blob=TextBlob(text_data)
        sentiment_score=blob.sentiment.polarity
        sentiment=''
        if sentiment_score > 0:
            sentiment='good'
        elif sentiment_score < 0:
            sentiment="Bad"
        else:
            sentiment="Neutral"
        
        data=json.loads(text_data)
        message=data.get('query','')
        time=data.get('time','')

        # storing the user memory
        memory.chat_memory.add_user_message(message)

        # generate response using langchain
        chain=prompt|llm|outputparser
        response = await chain.ainvoke({
            
            "message": message,
            "chat_history": memory.chat_memory.messages
        })

        #stores the ai messages
        memory.chat_memory.add_ai_message(response)

        await self.channel_layer.group_send(
             self.room_group_name,{
                  'type':'chat_message',
                  "sentiment_score":sentiment_score,
                  "quality":sentiment,
                  "time":time,
                  'message':response
             }
        )

        # send back a response
    
    async def chat_message(self,event):
        message=event['message']
        time = event.get('time', None)
        sentiment=event.get("quality",None)
        sentiment_score=event.get("sentiment_score",None)
        await self.send(text_data=json.dumps({
            'type':'chat',
            "sentiment_score":sentiment_score,
            "quality":sentiment,
            "time":time,
            'message':message
            }))
        
