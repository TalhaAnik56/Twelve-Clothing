import requests
import sys
import csv
import re
from html import unescape

def scrape_product(content,product_name,category_name):
    regular=regular_price_pat.findall(content)
    if len(regular)==0:
        regular=None
    else:
        regular=regular[0]     
    discounted=discounted_pat.findall(content)
    if len(discounted)==0:
        discounted=None
    else:
        discounted=discounted[0]    
    code_desc=code_desc_pat.findall(content)
    if len(code_desc)==0:
        product_code=None
        product_desc=None
    else:    
        code_desc=code_desc[0]
        product_code=code_desc[0]
        product_desc=code_desc[1]
        product_desc=unescape(product_desc)

    if regular==discounted:
        discounted="NO Discount"


    dict={"Product":product_name,"Category":category_name,"Regular Price":regular,"Discounted Price":discounted,"Code":product_code,"Material":product_desc}

    csv_writer.writerow(dict)



def get_next_page(content):
    res=next_page_pat.findall(content)

    if len(res)==0:
        return None
    res=res[0]
    res=host_name+res
    return res    

def get_product_list(content):
    result=product_pat.findall(content)
    return result

def crawl_category(category_name,category_url):
    while True:
        print(category_url)
        url_content=get_page_content(category_url)
        if url_content==None:
            break
        product_list=get_product_list(url_content)

        for product in product_list:
            product_url,product_name=product
            product_url=host_name+product_url
            content=get_page_content(product_url)
            product_name=unescape(product_name)
            scrape_product(content,product_name,category_name)
    
        next_page=get_next_page(url_content)
        if next_page==None:
            break
        category_url=next_page
    

def get_category(content):
    category_list=category_pat.findall(content)
    return category_list
    

def get_page_content(url):
    try:
        response=requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Couldn't collect the information from url:"+url)

    if response.ok:
        return response.text
    return None        


def crawl_website():
    url="https://twelvebd.com/"
    content=get_page_content(url)
    if content==None:
        sys.exit("Couldn't collect any information")

    category_list=get_category(content)
    for category in category_list:
        category_name,category_url=category
        category_name=unescape(category_name)
        category_url=host_name+category_url
        crawl_category(category_name,category_url)  
        



#main function starts here:
if __name__=="__main__":
    host_name="https://twelvebd.com"
    category_pat=re.compile(r'<h3 class="h4">(.+?)</h3>\s*<a href="(/collections/.+?)"',re.M|re.DOTALL)
    product_pat=re.compile(r'<a class="grid-view-item__link grid-view-item__image-container full-width-link" href="(/products/.*?)">\s*<span.+?">(.+?)</span>',re.M|re.DOTALL)
    next_page_pat=re.compile(r'<li class="pagination__text">.*?<a href="(/collections/.*?)" class=".*?">\s*<svg .*?<span class="icon__fallback-text">Next page</span>',re.M|re.DOTALL)
    regular_price_pat=re.compile(r'<s class="price-item price-item--regular" data-regular-price>\s*\D+([\d.,]+)\s*</s>',re.M|re.DOTALL)
    discounted_pat=re.compile(r'<span class="price-item price-item--sale" data-sale-price>\s*\D+([\d.,]+)\s*</span>',re.M|re.DOTALL)
    code_desc_pat=re.compile(r'<div class="product-single__description rte">\s*(.*?)<br>(.*?)<br>',re.M|re.DOTALL)
    
    with open("twelve_clothing.csv","w",newline="",encoding="utf-8")as f:
        csv_writer=csv.DictWriter(f,fieldnames=["Product","Category","Regular Price","Discounted Price","Code","Material"])
        csv_writer.writeheader()

        crawl_website()
        print("Crawling Done")