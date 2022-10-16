from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

driver = webdriver.Chrome()

# -----------------------Product Class----------------------------------

class myData:
    productName= ""
    productType= ""
    actualPrice= 0
    soldQuantity = 0
    discountPrice = 0
    ratings = 0.0
    totalReviews = 0
    
    def __init__(self, productName, productType,actualPrice,soldQuantity,discountPrice,ratings,totalReviews):
        self.productName = productName
        self.productType = productType
        self.actualPrice = actualPrice
        self.soldQuantity = soldQuantity
        self.discountPrice = discountPrice
        self.ratings = ratings
        self.totalReviews = totalReviews



# ---------This function will return page content------------------------------ 

def getPageSourceByURL(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    pageContent = driver.page_source
    soup = BeautifulSoup(pageContent, "html.parser")
    driver.quit()
    return soup






# ------------Global  Variables-------------------------------------------   
url = []
name = []
productsLinks = []
objectsList = []
pagesUrl = []
filePath = 'data.csv'




# -------This function will return categories List----------------------
def getCategoriesLinkFromMainPage():
    soup = getPageSourceByURL("https://www.daraz.pk/#")
    for link in soup.find_all('li',attrs={'class':'lzd-site-menu-sub-item'}):
        url.append(link.find('a')['href'])
        name.append(link.find('span').text)
    





# -------This function will return product links of given url---------
def getPoductsLinksFromCategoryPage(Url):
    soup = getPageSourceByURL(Url)
        
    for link in soup.find_all('div',attrs={'class':'title--wFj93'}):
        productsLinks.append(link.find('a')['href'])





# -------This function will return next page url---------------
def gotoNextPage(uRl,offset):
   Url = ""
   
   if (offset == 1):
     return "https:" + uRl + "?page=2"
   else:
       if(uRl[0] == 'h'):
           
           uRl = uRl.split("page=")
           Url = uRl[0] + "page=" + str(offset+1)
           
       else:
            uRl = uRl.split("page=")
            Url = "https:" + uRl[0] + "page=" + str(offset+5)
            
       return Url






# -------This function will scrap product and return product object and save in csv---------
def scrapProduct(url,category):
    soup = getPageSourceByURL(url)
    productName = (soup.find('span',attrs={'class':'pdp-mod-product-badge-title'}).text)
    totalReviews = (soup.find('a',attrs={'class':'pdp-link pdp-link_size_s pdp-link_theme_blue pdp-review-summary__link'}).text)
    discountedPrice = (soup.find('span',attrs={'class':'pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl'}).text)
    try:
        
        actualPrice = (soup.find('span',attrs={'class':'pdp-price pdp-price_type_deleted pdp-price_color_lightgray pdp-price_size_xs'}).text)
    
    except:
        actualPrice = discountedPrice
    try:
        rating = (soup.find('span',attrs={'class':'score-average'}).text)
    except:
        rating = 0.0
    print(productName)
    totalReviews = totalReviews.split(" ")
    if(totalReviews[0] == 'No'):
        totalReviews = 0
    else:
        
        totalReviews = int(totalReviews[0])
    discountedPrice = discountedPrice.split(" ")
    discountedPrice = (discountedPrice[1])
    actualPrice = actualPrice.split(" ")
    actualPrice = (actualPrice[1])
    if(len(discountedPrice) > 3):
        discountedPrice = discountedPrice.split(",")
        discountedPrice = int(discountedPrice[0] + discountedPrice[1])
        
    if(len(actualPrice) > 3):
        actualPrice = actualPrice.split(",")
        actualPrice = int(actualPrice[0] + actualPrice[1])
            
    soldQuantity = totalReviews
    myProduct = {
                    'Name': productName,
                    'Type': category,
                    'ActualPrice': actualPrice,
                    'discountedPrice': discountedPrice,
                    'Sold Quantity': soldQuantity,
                    'Reviews': totalReviews,
                    'Rating': rating    
        }

    return myProduct
# ----------This is the main Driver Function------------

def ScrapDataFromDaraz(n):
    start = 0
    getCategoriesLinkFromMainPage()
    for i in range (2,len(url)):
    
        getPoductsLinksFromCategoryPage("https:" + url[i])
        Link = url[i]
    
        for j in range(0,1):
        
        
            Link = gotoNextPage(Link,j+1)
            pagesUrl.append(Link)
            getPoductsLinksFromCategoryPage(Link)
    
        for k in range(start,len(productsLinks)):
            product = scrapProduct("https:"+ productsLinks[k], name[i])
            WriteIntoCsv(product, filePath)
            objectsList.append(product)
        
        start = len(productsLinks)
def WriteIntoCsv(NewEntry,filepath):
    df=pd.read_csv(filePath)
    if(len(df)>0):
        names=df['Name'].values.tolist()
        ActualPrices=df['Price'].values.tolist()
        price=df['Disc'].values.tolist()
        soldQuantity=df['SoldItems'].values.tolist()
        Reviews=df['Reviews'].values.tolist()
        Ratings=df['Ratings'].values.tolist()
        ItemType=df['Type'].values.tolist()
        #           Add new items into array
        names.append(NewEntry['Name'] )
        ActualPrices.append(NewEntry['Price'] )
        price.append(NewEntry['Disc'] )
        soldQuantity.append(NewEntry['SoldItems'] )
        Reviews.append(NewEntry['Reviews'] )
        Ratings.append(NewEntry['Ratings'] )
        ItemType.append(NewEntry['Type'] )
        dataBase={'Name': names,
                'Type':ItemType,
                'Price': ActualPrices,
                'Disc': price,
                'SoldItems': soldQuantity,
                'Reviews': Reviews,
                'Ratings': Ratings
                }
        df=pd.DataFrame(data=dataBase)
    else:
        # ['Name','Type','Price','Disc','SoldItems','Reviews','Ratings'
        data={'Name': [NewEntry['Name']] ,
                    'Price': [NewEntry['Price']],
                    'Disc': [NewEntry['Disc']],
                    'SoldItems': [NewEntry['SoldItems']],
                    'Reviews': [NewEntry['Reviews']],
                    'Ratings': [NewEntry['Ratings']],
                    'Type':[NewEntry['Type']]
                    }
        df=pd.DataFrame(data)
    df.to_csv(filePath)
    print('1 more data Add')

    
 
        
 
# ------------------Function Calls---------------------
ScrapDataFromDaraz(10)  
 