import argparse
import os
import re
import time

import zipfile

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException


class EtsyBot():
  def __init__(self, email, password, chromedriver_path):
    self.browserProfile = webdriver.ChromeOptions()
    self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    self.browser = webdriver.Chrome(chromedriver_path, options=self.browserProfile)
    self.email = email
    self.password = password
    
  def signIn(self):
    self.browser.get('https://www.etsy.com/signin')

    emailInput = self.browser.find_element(By.ID, 'join_neu_email_field')
    passwordInput = self.browser.find_element(By.ID, 'join_neu_password_field')

    emailInput.send_keys(self.email)
    passwordInput.send_keys(self.password)
    passwordInput.send_keys(Keys.ENTER)
    time.sleep(2)
  
  def createListing(self, images_to_upload, title, description, tags, price, files_to_upload):
    print('Creating listing.')
    self.browser.get('https://www.etsy.com/your/shops/me/tools/listings/create')
    time.sleep(5)
    
    # Upload listing images
    for image in images_to_upload:
      listingImage = self.browser.find_element(By.ID, 'listing-edit-image-upload')
      listingImage.location_once_scrolled_into_view
      listingImage.send_keys(image)
      time.sleep(1)
    time.sleep(5 * len(images_to_upload))
    
    # Set title
    titleInput = self.browser.find_element(By.ID, 'title')
    titleInput.location_once_scrolled_into_view
    titleInput.send_keys(title)
    time.sleep(1)
    
    # About this listing
    whoMadeDropdown = self.browser.find_element(By.ID, 'who_made')
    whoMadeDropdown.location_once_scrolled_into_view
    whoMadeInput = Select(whoMadeDropdown)
    whoMadeInput.select_by_visible_text('I did')
    time.sleep(1)
    
    whatIsDropdown = self.browser.find_element(By.ID, 'is_supply')
    whatIsDropdown.location_once_scrolled_into_view
    whatIsInput = Select(whatIsDropdown)
    whatIsInput.select_by_visible_text('A finished product')
    time.sleep(1)
    
    whenMadeDropdown = self.browser.find_element(By.ID, 'when_made')
    whenMadeDropdown.location_once_scrolled_into_view
    whenMadeInput = Select(whenMadeDropdown)
    whenMadeInput.select_by_index(2)
    time.sleep(1)
    
    # Category
    categoryInput = self.browser.find_element(By.ID, 'taxonomy-search')
    categoryInput.location_once_scrolled_into_view
    categoryInput.send_keys('Clip Art & Image Files')
    time.sleep(3)
    categoryInput.send_keys(Keys.ENTER)
    time.sleep(1)
    
    # Craft Type
    for i in range(1, 5):
      craftType = self.browser.find_element(By.XPATH, '//li[{}]/label/span'.format(i))
      craftType.location_once_scrolled_into_view
      craftType.click()
    
    # Type - set digital
    isDigitalRadio = self.browser.find_element(By.XPATH, "//p[contains(.,\'A digital file that buyers will download.\')]")
    isDigitalRadio.location_once_scrolled_into_view
    isDigitalRadio.click()
    time.sleep(1)

    # Set description
    descriptionInput = self.browser.find_element(By.ID, 'description')
    descriptionInput.location_once_scrolled_into_view
    descriptionInput.send_keys(description)
    time.sleep(1)
    
    # Section
    sectionDropdown = self.browser.find_element(By.ID, 'sections')
    sectionDropdown.location_once_scrolled_into_view
    sectionDropdown = Select(sectionDropdown)
    sectionDropdown.select_by_visible_text('SVGs')
    time.sleep(1)
    
    # Tags
    tagsInput = self.browser.find_element(By.ID, 'tags')
    tagsInput.location_once_scrolled_into_view
    for tag in tags:
      tagsInput.send_keys(tag)
      tagsInput.send_keys(Keys.ENTER)
      time.sleep(1)
    
    # Price
    priceInput = self.browser.find_element(By.ID, 'price_retail-input')
    priceInput.location_once_scrolled_into_view
    priceInput.send_keys(Keys.BACKSPACE)
    priceInput.send_keys(price)
    time.sleep(1)
    
    # Quantity
    quantityInput = self.browser.find_element(By.ID, 'quantity_retail-input')
    quantityInput.location_once_scrolled_into_view
    quantityInput.send_keys(Keys.BACKSPACE)
    quantityInput.send_keys('999')
    time.sleep(1)
    
    # Upload files
    for digital_file in files_to_upload:
      digitalFilesInput = self.browser.find_element(By.ID, 'listing-edit-digital-upload')
      digitalFilesInput.location_once_scrolled_into_view
      digitalFilesInput.send_keys(digital_file)
      time.sleep(1)
    time.sleep(10 * len(files_to_upload))
    
    # Publish
    publishButton = self.browser.find_element(By.XPATH, "//button[contains(.,\'Publish\')]")
    publishButton.location_once_scrolled_into_view
    publishButton.click()
    print('Please click publish in the browser to confirm.')
    time.sleep(20)

  def closeBrowser(self):
    self.browser.close()

  def __exit__(self, exc_type, exc_value, traceback):
    self.closeBrowser()

def main(args):
  
  print('Running publish_listing.py.\n')
  
  images_to_upload = []
  files_to_upload = []
  
  listing_dir_name = args.listing_dir.split('/')[-1]
  # Process files
  print('  Processing directory: {}/'.format(listing_dir_name))
  for root, _, files in os.walk(args.listing_dir, topdown=False):
    for name in files:
      full_path = os.path.join(root, name)
      if re.search(r'listing-photo.*\.(png|jpg)', name):
        images_to_upload.append(full_path)
      if re.search(r'downloads*/.*\.(eps|png|psd|svg)', full_path):
        files_to_upload.append(full_path)
  images_to_upload.sort()
  files_to_upload.sort()
  print('  Done processing.\n')
  
  print('  Zipping files.')
  zipfile_path = '/'.join([args.listing_dir, 'downloads.zip'])
  with zipfile.ZipFile(zipfile_path,'w', zipfile.ZIP_DEFLATED) as f: 
    # writing each file one by one 
    for file_path in files_to_upload: 
      f.write(file_path)
  print('  Done zipping files: {}.'.format(zipfile_path))
  
  title = ''
  tagline = ''
  tags = []
  price = ''
  
  # Gather user input
  while(True):
    # Title
    print('[Required] Enter a listing title, something like\n\tBaby Elephant SVG')
    title = input('Title: ')
    if not title:
      continue
    print()
    
    # Tagline
    print('[Optional] Enter a tagline, something like\n\tHow cute is this baby elephant?')
    tagline = input('Tagline: ')
    if not tagline:
      tagline = title
    print()
      
    # Description
    num_files = int(len(files_to_upload) // 4)
    description = '''{}
    
In this digital download, you'll receive the following in a zip file:

- {} EPS file
- {} SVG file
- {} PSD file
- {} PNG file

Works great with Cricut!

### Quotenote Cricut File Guarantee ###

Here at quotenote, we make sure that each file we sell works well with Cricut Design Space. After we design each file, we import the final SVG into Cricut Design Space ourselves to ensure that the file imports properly. We also do this to demonstrate to you on the second photo of every listing how the file will import into Cricut. This keeps our Etsy reviews high, our customers satisfied and ensures that you get your money's worth!

In the event that a file doesn't work as you thought it would, please reach out to us and we'd be happy to help. We check Etsy multiple times a day and are happy to respond!'''.format(tagline, num_files, num_files, num_files, num_files)
    
    # Tags
    i = 0
    tag_limit = 12
    print('[Required] Enter 12 tags, something like  baby elephant')
    while i < tag_limit:
      tag = input('Tag {} of {}: '.format(i+1, tag_limit))
      if tag:
        num_characters = len(tag)
        if num_characters > 20:
          print('Tag too long: limit 20 characters. You entered {} characters.'.format(num_characters))
          continue
        if tag in tags:
          print('You cannot use the same tag more than once')
          continue
        i += 1
        tags.append(tag)
      else:
        continue
    tags.append('quotenote')
    print()
    
    # Price
    print('[Optional] Enter a price, like  2.95')
    price = input('Price: $')
    if not price:
      price = '2.95'
    print()
      
    # Print the intended changes
    print('\n-------------INTENDED CHANGES-------------')
    ## Title
    print('\nTitle:')
    print(' - {}'.format(title))
    ## Description
    print('\nDescription:')
    for line in description.split('\n'):
      print('   {}'.format(line))
    ## Files to upload
    print('\nFiles to upload:')
    for filename in files_to_upload:
      print(' - {}'.format(filename))
    print('Uploading a single file: {}'.format(zipfile_path))
    ## Tags
    print('\nTags:')
    for tag in tags:
      print(' - {}'.format(tag))
    ## Price
    print('\nPrice:')
    print(' - ${}'.format(price))
    
    proceed = input('\nProceed? [y/n]: ')
    if proceed.lower() in ('y', 'yes'):
      break
    else:
      print('Restarting process.')
  
  print('Initializing eEtsyBot-2000 (v1.0.0)')
  print('''
  ╔═╗┌┬┐┌─┐┬ ┬╔╗ ┌─┐┌┬┐  
  ║╣  │ └─┐└┬┘╠╩╗│ │ │ 
  ╚═╝ ┴ └─┘ ┴ ╚═╝└─┘ ┴  v1.0.0  
''')
  
  etsy = EtsyBot(email=args.username, password=args.password, chromedriver_path=args.chromedriver_path)
  
  print('Signing in.')
  etsy.signIn()
  print('Signed in.')
  
  try:
    etsy.createListing(images_to_upload, title, description, tags, price, [zipfile_path])
  except Exception as e:
    print(e)
    time.sleep(25)
  print('Done.')
  
  time.sleep(10)
  

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Say hello')
  parser.add_argument('--username', required=True, type=str, help='Etsy username')
  parser.add_argument('--password', required=True, type=str, help='Etsy password')
  parser.add_argument('--listing_dir', required=True, type=str, help='Directory containing listing files')
  parser.add_argument('--chromedriver_path', required=True, type=str, help='Path to chromedriver executable. E.g.: /Users/michaelmcroskey/Documents/Development/etsy_utils/chromedriver')
  
  args = parser.parse_args()

  main(args)