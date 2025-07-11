import asyncio
from playwright.async_api import async_playwright
import pandas as pd
# step 1 scrape price and title

async def scrape_prices():
    async with async_playwright() as p:
        scraping = True  
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        page_number = 1
            
        await page.goto("https://www.flipkart.com/search?q=laptop", timeout=60000) 
        await page.wait_for_selector("div:has-text('Chromebook')") #Playwright pseudo-class extension
        data = []

        
        while scraping: 
            #This XPath selector:
            titles = page.locator("//div[contains(text(),'Chromebook') or contains(text(),'Laptop') or contains(text(),'ASUS') or contains(text(),'Lenovo')]")
            prices = page.locator("//div[contains(text(),'₹')]")
            
            count = await titles.count()
            
            for i in range(count):
                title = await titles.nth(i).text_content()
                try:
                    price = await prices.nth(i).text_content()
                except:
                    print(f"Price not found for item{i}")
                    continue
                
                if title and price:
                    data.append(
                        {
                            "title": title.strip(),
                            "price": price.strip().replace("₹","").replace(",","")
                        }
                    )
            next_locater = page.locator("span:has-text('Next')")
            count = await next_locater.count()
            if count>0:
                # save the title before clcik
                first_title_before = await titles.first.text_content()
                await next_locater.click()
                await page.wait_for_timeout(3000)  # give time to load next page
                
                # Refresh titles after click
                titles = page.locator("//div[contains(text(),'Chromebook') or contains(text(),'Laptop') or contains(text(),'ASUS') or contains(text(),'Lenovo')]")
                first_title_after = await titles.first.text_content()
                
                if first_title_before == first_title_after:
                    print("No Change after clicking next - last page reached")
                    break
                else:
                    page_number += 1
                    print(f"Page number {page_number}")
                
            else:
                print("Next button not found -> Ending Scraping")
                break
        await browser.close()
        return pd.DataFrame(data)
        
    
    
# Step_2 Clean the Data

def clean_prices(df):
    df = df.copy()
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna()
    df = df[df['price'] > 1000] #Remove unwanted Noices
    return df


async def main():
    print("SCRAPING___STARTED_____")
    df_raw = await scrape_prices()
    
    print("CLEANING__DATA____")
    df_clean = clean_prices(df_raw)
    
    print("SAVING TO CSV")
    df_clean.to_csv("Flipkart_prices.csv", index= False)
    print(df_clean.head())
    
    

            
if __name__ == "__main__":
    asyncio.run(main())
