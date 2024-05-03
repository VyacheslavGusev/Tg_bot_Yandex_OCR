from openai import OpenAI

# Создаем экземпляр клиента с вашим API ключом
client = OpenAI(
    api_key="sk-proj-B0fRRnN2MZmTYQilFATzT3BlbkFJ235AAVa3wJ5cSLHEGRNg",
    base_url="https://api.oai.synergy.ru/v1/",
)

def chat_gender(df_res, column_name):
    # Список для хранения определенных полов
    genders = []
    
    for full_name in df_res[column_name]:
        messages = [
            {"role": "user", "content": f'{full_name} Определи пол этого человека ответь одной буквой: М или Ж'}
        ]
        
        # Отправляем запрос к нейросети
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages
        )
        
        # Получаем ответ от нейросети
        response_message = chat_completion.choices[0].message.content
        
        
        genders.append(response_message)
    
    # Возвращаем список определенных полов
    return genders