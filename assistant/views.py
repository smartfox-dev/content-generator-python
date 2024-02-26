# importing render and redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Articles
# importing the openai API
from .secret_key import API_KEY
import openai
import requests

# selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

# scrapping 
from bs4 import BeautifulSoup
# from webdriver_manager.chrome import ChromeDriverManager

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# YAML_FILE_PATH = os.path.join(BASE_DIR, 'google_keyword.yml')
# print('YAML file path', YAML_FILE_PATH)
# serarch/ keywords volume
from google.ads.googleads.client import GoogleAdsClient
# client = GoogleAdsClient.load_from_storage(YAML_FILE_PATH)
# import the generated API key from the secret_key file

# Configure Chrome options for headless browsing
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

# loading the API key from the secret_key file
openai.api_key = API_KEY

index = 0
title = "What Tools Do I Need to Change a Flat Tire? A Detailed Checklist"
topic = "Essential tools needed for changing a flat tire"
keyword = "Essential Tools for Tire Change"
tone = "Professional"
sciamount = 0
word_count = 500
language = "davinci"
# language = "English"
result = []
article = "What Tools Do I Need to Change"
soup123 = requests.session()
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
# this is the home view for handling home page logic

# overview page start
ov_searchtype = "Topic"
# ov_searchtype = "Date"
ov_keyword = ""
ov_sort = 1
ov_delete_id = None
# overview page end
def openai_function(prompt, temperature):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        max_tokens=6500,
        temperature=temperature,
        messages = prompt
    )
    return response['choices'][0]['message']['content']

def generate(request):
    if request.method == 'POST':
        global topic, title, keyword, tone, sciamount, language, word_count, input_urls
        language = request.POST.get('language') or language
        topic = request.POST.get('topic') or topic
        title = request.POST.get('title') or title
        sciamount = request.POST.get('sciamount') or sciamount
        keyword = request.POST.get('keyword') or keyword
        word_count = request.POST.get('word_count') or word_count  
        input_urls = request.POST.getlist('input_url')  
    
    print("=======********====generate:",index, title, keyword, tone, language, word_count)
    print("=======input_urls:", input_urls)
    print("=======generate_driver_content:", driver)
    
    # python scrapping about selected urls start
    input_url_contents = ""
    for input_url in input_urls:
        print("each_input_url:", input_url)
        if input_url:
            driver.get(input_url)
            # wait = WebDriverWait(driver, 10)
            # form_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form[target="_self"]')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')  # Parsing content using beautifulsoup
            content = soup.select('body')[0].text
            content = content.replace("\n", "")
            content = content[300:600]
            input_url_prompt = []
            if content:
                input_url_content = "Please provide 50 words basic scientific sentences or concepts from this content:" + content
                input_url_prompt.append({"role": "user", "content": input_url_content})
                print("input_url_prompt:", input_url_prompt)
                response = openai_function(input_url_prompt, 1)
                
                print('response:', response)
                input_url_contents += response
            
    print("input_url_contents:", input_url_contents) 
    input_url_contents = input_url_contents[:250]
    # input_url_contents = "Please write with reference to this sentence:" + input_url_contents
    temp_url_content = ''
    if input_url_contents:
        total_url_content = "Please provide me 50 scientific words from this sentence:" + input_url_contents
        total_url_prompt = []
        total_url_prompt.append({"role": "user", "content": total_url_content})
        print("input_url_prompt:", total_url_prompt)
        temp_url_content = openai_function(total_url_prompt, 0.5)
        temp_url_content = temp_url_content[:200]
        temp_url_content = "Please write an article by combining this content:" + temp_url_content + ""
        print('response:', temp_url_content)
    # python scrapping about select urls end 
        
    # global condition prompt
    if language == "English":
        condition_prompt= "Please continue writing until the conclusion reaches " + str(int(int(word_count) / 4)) + " words."
    elif language == "Dutch":
        condition_prompt= "Ga door met schrijven totdat de conclusie is bereikt " + str(int(int(word_count) / 4)) + " woorden."
    # prompt array1 
    prompt_array1 = []
    if language == "English":
        prompt1 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nPlease generate introduction that consists of exactly " + str(int(int(word_count) / 4)) + " words article based on this prompt."
    elif language == "Dutch":
        prompt1 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nGenereer een introductie die precies bestaat uit " + str(int(int(word_count) / 4)) + " woorden artikel gebaseerd op deze prompt."
    print("===first_prompt:", prompt1)
    prompt_array1.append({"role": "user", "content": prompt1})
    if temp_url_content:
        prompt_array1.append({"role": "user", "content": temp_url_content})
     # global condition prompt
    if language == "English":
        condition_prompt= "Please continue writing until the conclusion reaches " + str(int(int(word_count) / 4)) + " words."
    elif language == "Dutch":
        condition_prompt= "Ga door met schrijven totdat de conclusie is bereikt " + str(int(int(word_count) / 4)) + " woorden."
    prompt_array1.append({"role": "user", "content": condition_prompt})
    print("prompt_array1:", prompt_array1)
    formatted_response1 = openai_function(prompt_array1, 1)
    print("formatted_response1:", formatted_response1)
    
    # prompt array2 
    prompt_array2 = []
    if language == "English":
        prompt2 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 3)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nPlease generate background or context that consist of exactly " + str(int(int(word_count) / 3)) + " words article based on this prompt."
    if language == "Dutch":
        prompt2 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 3)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nGenereer een achtergrond of context die precies bestaat uit: " + str(int(int(word_count) / 3)) + " woorden artikel gebaseerd op deze prompt."
    print("===first_prompt:", prompt2)
    prompt_array2.append({"role": "user", "content": prompt2})
    if temp_url_content:
        prompt_array2.append({"role": "user", "content": temp_url_content})
     # global condition prompt
    if language == "English":
        condition_prompt= "Please continue writing until the conclusion reaches " + str(int(int(word_count) / 3)) + " words. No repeat the same words and text with the mentioned above sentence."
    elif language == "Dutch":
        condition_prompt= "Ga door met schrijven totdat de conclusie is bereikt " + str(int(int(word_count) / 3)) + " woorden."
    prompt_array2.append({"role": "user", "content": condition_prompt})
    print("prompt_array2:", prompt_array2)
    formatted_response2 = openai_function(prompt_array2, 1)
    print("formatted_response2:", formatted_response2)
    
    # prompt array3 
    prompt_array3 = []
    if language == "English":
        prompt3 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 3)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nPlease generate body that consist of exactly " + str(int(int(word_count) / 3)) + " words article based on this prompt."
    if language == "Dutch":
        prompt3 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 3)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nGenereer een hoofdtekst die precies uit bestaat " + str(int(int(word_count) / 3)) + " woorden artikel gebaseerd op deze prompt."
    print("===first_prompt:", prompt3)
    prompt_array3.append({"role": "user", "content": prompt3})
    if temp_url_content:
        prompt_array3.append({"role": "user", "content": temp_url_content})
     # global condition prompt
    if language == "English":
        condition_prompt= "Please continue writing until the conclusion reaches " + str(int(int(word_count) / 3)) + " words. No repeat the same words and text with the mentioned above sentence."
    elif language == "Dutch":
        condition_prompt= "Ga door met schrijven totdat de conclusie is bereikt " + str(int(int(word_count) / 3)) + " woorden."
    prompt_array3.append({"role": "user", "content": condition_prompt})
    print("prompt_array3:", prompt_array3)
    formatted_response3 = openai_function(prompt_array3, 1)
    print("formatted_response3:", formatted_response3)
    
    # prompt array4
    prompt_array4 = []
    if language == "English":
        prompt4 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nPlease generate supporting evidence or examples that consist of exactly " + str(int(int(word_count) / 4)) + " words article based on this prompt."
    if language == "Dutch":
        prompt4 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nGenereer ondersteunend bewijsmateriaal of voorbeelden die precies bestaan uit " + str(int(int(word_count) / 4)) + " woorden artikel gebaseerd op deze prompt."
    print("===first_prompt:", prompt4)
    prompt_array4.append({"role": "user", "content": prompt4})
    if temp_url_content:
        prompt_array4.append({"role": "user", "content": temp_url_content})
     # global condition prompt
    if language == "English":
        condition_prompt= "Please continue writing until the conclusion reaches " + str(int(int(word_count) / 4)) + " words. No repeat the same words and text with the mentioned above sentence."
    elif language == "Dutch":
        condition_prompt= "Ga door met schrijven totdat de conclusie is bereikt " + str(int(int(word_count) / 4)) + " woorden."
    prompt_array4.append({"role": "user", "content": condition_prompt})
    print("prompt_array4:", prompt_array4)
    formatted_response4 = openai_function(prompt_array4, 1)
    print("formatted_response4:", formatted_response4)
    
    # prompt array5 
    prompt_array5 = []
    if language == "English":
        prompt5 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nPlease generate future directions that consist of exactly " + str(int(int(word_count) / 4)) + " words article based on this prompt. continue writing until the number of words that used in this article be exactly " + str(int(int(word_count) / 4))
    if language == "Dutch":
        prompt5 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nGenereer toekomstige aanwijzingen die precies uit " + str(int(int(word_count) / 4)) +  " woorden artikel gebaseerd op deze prompt. ga door met schrijven totdat het aantal woorden dat in dit artikel wordt gebruikt exact is " + str(int(int(word_count) / 4)) + " remove number in text"
    print("===first_prompt:", prompt5)
    prompt_array5.append({"role": "user", "content": prompt5})
    if temp_url_content:
        prompt_array5.append({"role": "user", "content": temp_url_content})
     # global condition prompt
    if language == "English":
        condition_prompt= "Please continue writing until the conclusion reaches " + str(int(int(word_count) / 4)) + " words. No repeat the same words and text with the mentioned above sentence."
    elif language == "Dutch":
        condition_prompt= "Ga door met schrijven totdat de conclusie is bereikt " + str(int(int(word_count) / 4)) + " woorden."
    prompt_array5.append({"role": "user", "content": condition_prompt})
    print("prompt_array5:", prompt_array5)
    formatted_response5 = openai_function(prompt_array5, 1)
    print("formatted_response5:", formatted_response5)
    
    # prompt array6 
    prompt_array6 = []
    if language == "English":
        prompt6 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\nPlease generate conclusion that consist of exactly " + str(int(int(word_count) / 4)) + " words article based on this prompt."
    if language == "Dutch":
        prompt6 = "Topic: " + str(topic) + ".\nTitle: " + str(title) + ".\nKeyword: " + str(keyword) + ".\nLanguage: " + str(language) + ".\nWord count: " + str(int(int(word_count) / 4)) + ".\nScientific Literature: " + str(sciamount) + ".\nStyle: " + str(tone) + "\Genereer een conclusie die precies bestaat uit " + str(int(int(word_count) / 4)) + " woorden artikel gebaseerd op deze prompt."
    print("===first_prompt:", prompt6)
    prompt_array6.append({"role": "user", "content": prompt6})
    if temp_url_content:
        prompt_array6.append({"role": "user", "content": temp_url_content})
     # global condition prompt
    if language == "English":
        condition_prompt= "Please continue writing until the conclusion reaches " + str(int(int(word_count) / 4)) + " words. No repeat the same words and text with the mentioned above sentence."
    elif language == "Dutch":
        condition_prompt= "Ga door met schrijven totdat de conclusie is bereikt " + str(int(int(word_count) / 4)) + " woorden."
    prompt_array6.append({"role": "user", "content": condition_prompt})
    print("prompt_array6:", prompt_array6)
    formatted_response6 = openai_function(prompt_array6, 1)
    print("formatted_response6:", formatted_response6)
    
    article ="-" + title + "\n\n" + formatted_response1 + "\n" + formatted_response2 + formatted_response3 + "\n" + formatted_response4 + "\n" + formatted_response5 + "\n" + formatted_response6
    
    
    articleModal = Articles()
    articleModal.title = title
    articleModal.topic = topic
    articleModal.keyword = keyword
    articleModal.word_count = word_count
    articleModal.content = article
    articleModal.save()
    
    print("formatted_response:", article)
    
    context = {
            'index': index,
            'article': article,
            'messages': request.session['messages'],
            'topic' : topic,
            'title' : title,
            'keyword' : keyword,
            'language': language,
            'word_count': word_count,
    }
    return render(request, 'assistant/home.html', context)

def home(request):
    try:
        # if the session does not have a messages key, create one
        if 'prompts' not in request.session:
            request.session['prompts'] = []

        if 'messages' not in request.session:
            request.session['messages'] = []

        if request.method == 'POST':
            global index, topic, title, keyword, tone, sciamount, language, word_count
            topic = request.POST.get('topic') or topic
            language = request.POST.get('language') or language
            print("forward_language:", language)
            # get the prompt from the form
            input= request.POST.get('input')
            temperature = 0.1

            request.session['messages'].append({"role": "user", "content": input})
            if index == 0 and language == "English":
                prompt = "This is my topic." + input + ". Give me 10-15 long tail topics with high search volume which people search a lot and trending based on my topic."
            elif index == 0 and language == "Dutch":
                prompt = "Dit is mijn onderwerp." + input + ". Geef mij 10-15 long tail-onderwerpen met een hoog zoekvolume, waar mensen veel naar zoeken en die trending zijn op basis van mijn onderwerp."
            if index == 1 and language == "English":
                prompt = "This is my topic." + input + ". Give me 3 different titles with high search volume which people search a lot and trending based on my topic."
                result.append(input)
                topic = input
            elif index == 1 and language == "Dutch":
                prompt = "Dit is mijn onderwerp." + input + ". Geef me 3 verschillende titels met een hoog zoekvolume waar mensen veel naar zoeken en die trending zijn op basis van mijn onderwerp."
                result.append(input)
                topic = input

            if index == 2 and language == "English":
                prompt = "This is my title." + input + ". Provide best 10 keywords with high search volume which people search a lot and trending to use for SEO purposes based on my title"
                result.append(input)
                title = input
            elif index == 2 and language == "Dutch":
                prompt = "Dit is mijn onderwerp." + input + ".Bied de beste 10 zoekwoorden met een hoog zoekvolume waarnaar mensen veel zoeken en die populair zijn om te gebruiken voor SEO-doeleinden op basis van mijn titel."
                result.append(input)
                title = input

            if index == 3 and language == "English":
                prompt = "If desired, scientific articles can be integrated into the article. Visit <a class='alink' href='https://pubmed.ncbi.nlm.nih.gov/' target='_blank'>https://pubmed.ncbi.nlm.nih.gov/</a> or <a class='alink' href='https://scholar.google.com/' target='_blank'>https://scholar.google.com/</a>, then enter the selected URLs into our scraper."
                result.append(input) 
                keyword = input
            elif index == 3 and language == "Dutch":
                prompt = "Als gewenst kunnen wetenschappelijke artikels worden geïntegreerd in het artikel. Bezoek <a class='alink' href='https://pubmed.ncbi.nlm.nih.gov/' target='_blank'>https://pubmed.ncbi.nlm.nih.gov/</a> of <a class='alink' href='https://scholar.google.com/' target='_blank'>https://scholar.google.com/</a>, en voer vervolgens de geselecteerde URL's in in onze scraper."
                result.append(input)
                keyword = input
                
            print("===prompt:", prompt)
            # format the response
            request.session['prompts'].append({"role": "user", "content": prompt})
            if index != 3:
                formatted_response = openai_function(request.session['prompts'], 0.5)
            elif index == 3:
                formatted_response = prompt
            print("pre_formatted_response: " + formatted_response)
            if index == 0 and language == "English":
                formatted_response += "\nThese are the topics with high search volume which people search a lot and trending. Choose one of the topics."
            elif index == 0 and language == "Dutch":
                formatted_response += "\nDit zijn de onderwerpen met een hoog zoekvolume waar mensen veel naar zoeken en trending zijn. Kies een van de onderwerpen."
            if index == 1 and language == "English":
                formatted_response += "\nThese are the three titles with high search volume which people search a lot and trending. Choose one of the titles."
            elif index == 1 and language == "Dutch":
                formatted_response += "\nDit zijn de drie titels met een hoog zoekvolume waar mensen veel naar zoeken en trending zijn. Kies een van de titels."

            if index == 2 and language == "English":
                formatted_response += "\nThese are the best keywords with high search volume which people search a lot and trending. Choose one of the keywords."
            elif index == 2 and language == "Dutch":
                formatted_response += "\nDit zijn de beste zoekwoorden met een hoog zoekvolume waar mensen veel naar zoeken en trending zijn. Kies een van de trefwoorden."

            print("===index:", index, "====for_formatted_response:", formatted_response)
            # append the response to the messages list
            request.session['prompts'].append({"role": "assistant", "content": formatted_response})
            request.session['messages'].append({"role": "assistant", "content": formatted_response})
            # append the response to the messages list

            request.session.modified = True
            print("selected_language:", language)
            # redirect to the home page
            context = {
                'index': index,
                'messages': request.session['messages'],
                # 'result' : result,
                'topic' : topic,
                'title' : title,
                'keyword' : keyword,
                'language': language,
                'word_count': word_count,
            }
            index += 1

            return render(request, 'assistant/home.html', context)
        else:
            # if the request is not a POST request, render the home page
            context = {
                'messages': request.session['messages'],
                'temperature': 0.1,
            }
            return render(request, 'assistant/home.html', context)
    except Exception as e:
        print(e)
        # if there is an error, redirect to the error handler
        return redirect('error_handler')

def loading(request):
    return render(request, 'assistant/loading.html')

def overview(request):
    try:
        print("overviewprint:", request)
        global ov_searchtype, ov_keyword, ov_sort, ov_delete_id
        ov_searchtype = request.POST.get('ov_searchtype')
        ov_keyword = request.POST.get('ov_keyword')        
        ov_sort = int(request.POST.get('ov_sort', 1))  # Assuming a default value of 0 if 'ov_sort' is not provided
        ov_delete_id = request.POST.get('ov_delete_id')

        if ov_searchtype == None:
            ov_searchtype = "Topic"
        if ov_keyword == None:
            ov_keyword = ""
        print("----overview searchtype----:", ov_searchtype)
        print("----overview keyword----:", ov_keyword)
        print("----overview sort----:", ov_sort)
        print("----overview delete id----", ov_delete_id)
        
        if ov_delete_id != None:
            try:
                table_to_delete = get_object_or_404(Articles, id=ov_delete_id)
                table_to_delete.delete()
            except Exception as e:
                print("overview page:", e)
                # if there is an error, redirect to the error handler
                return redirect('error_handler')
            
        sort_expression = 'created_at' if ov_sort >= 0 else '-created_at'
        table_array = Articles.objects.all().order_by(sort_expression)
        
        if ov_searchtype and ov_keyword:
            if ov_searchtype == "Topic":
                print("-------------------------")
                table_array = table_array.filter(topic__icontains=ov_keyword)
            elif ov_searchtype == "Date":
                table_array = table_array.filter(created_at__icontains=ov_keyword)
        print("formatted_articles:", table_array)
        if table_array:
            formatted_array = [
                {   'id': item.id,
                    'title': item.title,
                    'topic': item.topic,
                    'keyword': item.keyword,
                    'word_count': item.word_count,
                    'created_at': item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'content': item.content
                }
                for item in table_array
            ]
        else:
            formatted_array = []
        context = {
            'table_array': formatted_array,
            'ov_searchtype': ov_searchtype,
            'ov_keyword': ov_keyword,
            'ov_sort': ov_sort
        }
        return render(request, 'assistant/overview.html', context)
        # article = Articles()
        # article.title = "Computer Hacking"
        # article.topic = "What technologies can I use this implement it"
        # article.keyword = "Computer Science"
        # article.word_count = 1500
        # article.save()

        # table_array = []
        # for i in range(100):
        #     item = {
        #         'field1': f'field{i}',
        #         'field2': f'field{i}',
        #         'field3': f'field{i}',
        #         'field4': f'field{i}',
        #     }
        #     table_array.append(item)
        # context = {
        #     'table_array': table_array,
        # }
        
        # return render(request, 'assistant/overview.html', context)
    except Exception as e:
        print("overview page:", e)
        # if there is an error, redirect to the error handler
        return redirect('error_handler')
        
def new_chat(request):
    global index
    # clear the messages list
    request.session.pop('prompts', None)
    request.session.pop('messages', None)
    index = 0
    return redirect('home')


# this is the view for handling errors
def error_handler(request):
    return render(request, 'assistant/404.html')
