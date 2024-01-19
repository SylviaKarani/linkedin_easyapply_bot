from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException,StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time, random, logging, datetime

import pyautogui
from config import parameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class LinkedInBot:
    def __init__(self, parameters):
        self.parameters = parameters 
        self.email = parameters['email']
        self.first_name = parameters['first_name']
        self.last_name = parameters['last_name']
        self.country_code = parameters['country_code']
        self.mobile_phone_number = parameters['mobile_phone_number']
        self.phone = parameters["phone"]
        self.password = parameters['password']
        self.street_address_line_1 = parameters['street_address_line_1']
        self.city = parameters['city']
        self.zip_postal_code= parameters['zip_postal_code']
        self.state = parameters['state']
        self.disable_lock = parameters['disableAntiLock']
        self.positions = parameters.get('positions', [])
        self.locations = parameters.get('locations', [])
        self.years_of_work_experience = parameters.get('years_of_work_experience', 0)
        self.years_of_experience_in = parameters.get('years_of_experience_in', 0)
        self.salary= parameters.get('expected_salary', 0)
        self.completed_bachelor_degree=parameters.get('completed_bachelor_degree',[])
        self.proficiency_in_english=parameters.get('english_proficiency',[])
        self.num_jobs_to_apply = parameters.get('num_jobs_to_apply', 0)
        self.base_search_url = self.get_base_search_url(parameters)
        
        self.filters_applied = False

        chrome_driver_path = ChromeDriverManager().install()
        service = Service(executable_path= chrome_driver_path)
        
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features")
        options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")  
        
        self.driver = webdriver.Chrome(service=service, options=options)
     

    def login(self):
        try:
            self.driver.set_window_size(1200, 800)
            
            
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(5, 10))
            self.driver.find_element(By.ID, "username").send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.CSS_SELECTOR,".btn__primary--large").click()
            time.sleep(random.uniform(5, 10))
            
            print("Login button Clicked!")
            
            # Check for security check after pressing login button
            self.security_check()
             
            time.sleep(random.uniform(5, 10))
            # Use WebDriverWait to wait for the presence of an element after successful login
            WebDriverWait(self.driver, 20).until(
                EC.url_matches("https://www.linkedin.com/feed/")
            )

            print("Login successful!")
            
            self.driver.save_screenshot('after_login.png')
            print("Screenshot saved!")
            
        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            self.driver.save_screenshot("cldntlogin.png")
            raise Exception("Could Not Log In!")
         

        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred during login!")
        self.driver.save_screenshot('after_login.png')  
       
    def security_check(self):
        current_url = self.driver.current_url
        page_source = self.driver.page_source

        if '/checkpoint/challenge/' in current_url or 'security check' in page_source:
            print(f"Security check detected.")
            input("Press Enter in this console when the security check is done.")
            time.sleep(random.uniform(5.5, 10.5))
                
    def apply_filters(self):
        try:

            logger.info("CLicking Jobs button")
            time.sleep(random.uniform(5, 10))
            # Click on the "Jobs" button to go to the Jobs section
            jobs_button = WebDriverWait(self.driver, 150).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.linkedin.com/jobs/?']"))
                )
            jobs_button.click()
            
            print("In Job Page")
            time.sleep(random.uniform(5, 10))
            self.driver.save_screenshot('job_page.png')
            

            # Input job title
            title_input = WebDriverWait(self.driver, 150).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")))
            time.sleep(random.uniform(5, 10))
            
            
            title_input.send_keys(self.positions[0])
            print("entered job title")
            
            title_input.send_keys(Keys.RETURN)
            # After pressing Enter
            self.driver.save_screenshot("entered_job_search.png")
            
            print("Input search value and pressed enter")
            
            # Get the base search URL
            search_url = self.get_base_search_url(self.parameters)
            self.driver.get(search_url)

            
            # Wait for the search page to load
            WebDriverWait(self.driver, 150).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-search-results-list"))
            )

            # Capture screenshot after the search results have loaded
            self.driver.save_screenshot('after_search.png')
            print("Screenshot saved!")
            
            time.sleep(random.uniform(20, 20))

            logger.info("Clicking on Easy Apply")

            self.apply_easy_apply_filter()

            
            
            
        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            logger.error(f"Current URL: {self.driver.current_url}")
            raise Exception("An unexpected error occurred while applying filters.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while applying filters.")

    def apply_to_job(self):
        try:
            logger.info("Starting Jobs Application")
            time.sleep(random.uniform(5, 10))

            time.sleep(random.uniform(5, 10))
            #Find element that contains the total numbet of jobs
            total_jobs_element = WebDriverWait(self.driver, 250).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,"div.jobs-search-results-list__subtitle span" ))

            ) 

            total_jobs_text = total_jobs_element.text
            total_jobs = int(total_jobs_text.split()[0])

            if total_jobs == 0:
                print("No Jobs Found")
                return
            else:
                print(f"Total {total_jobs} jobs found.")
                self.driver.save_screenshot("Number_of_jobs.png")
             
            time.sleep(random.uniform(5, 10))
            #Iterate through each job listing
            jobs_listings = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
            
            for job_listing in jobs_listings:
                self.apply_to_job_listing(job_listing)
                self.driver.save_screenshot("job_clicked.png")

        
        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("An unexpected error occurred while checking and applying to jobs.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while checking and applying to jobs.")

    def apply_to_job_listing(self,job_listing):
        try:

            while self.num_jobs_to_apply > 0:
                self.apply_to_next_job(job_listing)
                self.num_jobs_to_apply -= 1

            logger.info(f"Applied to {self.num_jobs_to_apply} jobs successfully!")

        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("An unexpected error occurred while applying to job listings.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while applying to job listings.")
    
    def apply_to_next_job(self, job_listing):
        try:

            job_list_container = WebDriverWait(self.driver, 250).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__list-container"))
            )

            job_listings = job_list_container.find_elements(By.CSS_SELECTOR, "a.job-card-list__title")
            
            if not job_listings:
                logger.warning("No more visible jobs. Scrolling down.")
                self.scroll_down()
            
            for job_listing in job_listings:
                job_listing.click()
                logger.info("Job Clicked")
                time.sleep(random.uniform(5, 10))
                self.driver.save_screenshot("job_clicked.png")
                time.sleep(random.uniform(5, 10))

                # Wait for job details to load
                WebDriverWait(self.driver, 300).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-job-id][aria-label^='Easy Apply']"))
                )
                time.sleep(random.uniform(5, 10))

                # Optionally, check filters if they are applied
                if not self.are_filters_applied():
                    print("No filters applied. Continue with the job application process.")
                else:
                    self.filter_job(job_listing)

                # Click on easy apply button
                easy_apply_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-job-id][aria-label^='Easy Apply']")
                easy_apply_button.click()
                logger.info("EASY APPLY CLICKED")
                self.driver.save_screenshot("easy_apply_clicked.png")

                # Wait for the Easy Apply form to load (you may need to adjust the waiting time)
                form_element = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping'))
                )
                 
                time.sleep(random.uniform(5, 10))

                # Simulate the process of filling out the Easy Apply form
                if form_element:
                    logger.info("Easy Apply form loaded")
                    self.fill_easy_apply_form()
                else:
                    self.scroll_slow(form_element)
                    logger.info("Easy apply form there")
                    logger.info("started filling form")
                    self.fill_easy_apply_form()

                time.sleep(random.uniform(20, 30))

                # After submitting the application, you might want to capture a screenshot or perform additional actions
                self.driver.save_screenshot('application_submitted.png')
                print("Application submitted successfully!")
                

                self.scroll_slow(job_list_container) 
                # Go back to the search results page for the next job
                self.driver.execute_script("window.history.go(-1)")
        
        except StaleElementReferenceException:
            # Handle stale element reference by finding the element again
            logger.warning("StaleElementReferenceException. Trying to find the element again.")
            self.apply_to_next_job(job_listing)  # Recursive call to try again

        except NoSuchElementException:
            logger.warning("No more visible jobs. Scrolling down.")
            self.scroll_down()

    def scroll_down(self):
        # Scroll down to load more jobs or move to the next page
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def scroll_slow(self, scrollable_element, start=0, end=3600, step=100, reverse=False):
        if reverse:
            start, end = end, start
            step = -step

        for i in range(start, end, step):
            self.driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollable_element)
            time.sleep(random.uniform(1.0, 2.6))

    def go_to_next_page(self):
        # Wait for the next page button to be clickable
        next_page_button = WebDriverWait(self.driver, 250).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li[data-test-pagination-page-btn].artdeco-pagination__indicator--number + li"))
        )
        next_page_button.click()
    
    def fill_easy_apply_form(self):
        try:
            logger.info("Start filling easy apply form")
            while True:
                time.sleep(random.uniform(20, 30))
               

                # Find the section header to determine the type of section
                section_header = None
                try_count = 0
                while try_count < 3:  # Try a maximum of 3 times to find the section header
                    try:
                        section_header = WebDriverWait(self.driver, 200).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'pb4'))
                        )
                        break  # If successful, exit the loop
                    except TimeoutException:
                        # Scroll down and try again
                        self.scroll_down()
                        try_count += 1

                if not section_header:
                    self.dismiss_modal()
                    raise NoSuchElementException("Section header not found after multiple attempts.")                   
                    
                # Extract the section label
                section_label = section_header.find_element(By.TAG_NAME, 'h3').text.lower()
                logger.info(f"Looking for title of form: {section_label}")

                if 'contact info' in section_label:
                    self.apply_contact_info()
                    logger.info("Contact info filled")

                elif 'resume' in section_label:
                    self.upload_resume()
                    logger.info("resume section filled")

                elif 'additional questions' in section_label:
                    self.dismiss_modal()
                    logger.info("additional questions answered")

                elif 'review your application' in section_label:
                    self.scroll_to_submit_button()
                    logger.info("review done")
                
                elif 'home address' in section_label:
                    self.apply_home_address()
                    logger.info("home address filled")

                else:
                    logger.warning(f"Unknown section: {section_label}")
                    self.dismiss_modal()
                    logger.info("Unknown Section")

        except (TimeoutException, WebDriverException, NoSuchElementException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("An unexpected error occurred while filling easy apply.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while filling easy apply.")
    
    def dismiss_modal(self):
        # Find the dismiss button and click it
        dismiss_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Dismiss"]'))
        )
        dismiss_button.click()

        # Wait for the discard button to appear and click it
        discard_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-control-name="discard_application_confirm_btn"]'))
        )
        discard_button.click()

    def apply_contact_info(self):
        try:
            # Wait for form to load
            logger.info("start filling contact info")
            form_element = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping'))
            )

            time.sleep(random.uniform(20, 30))
            labels_to_search = ["First name", "Last name", "Mobile phone number", "Phone"]

            for label_to_search in labels_to_search:
                try:
                    input_field = self.driver.find_element(
                        By.XPATH, f'//label[contains(text(), "{label_to_search}")]/following-sibling::input'
                    )
                    if not input_field.get_attribute('value') and getattr(self, label_to_search.lower().replace(" ", "_")):
                        input_field.send_keys(getattr(self, label_to_search.lower().replace(" ", "_")))
                
                except NoSuchElementException:
                    logger.warning(f"Input field for '{label_to_search}' not found.")
                    time.sleep(random.uniform(20, 30))
            
            time.sleep(random.uniform(20, 30))
            self.driver.save_screenshot("contact.png")
            time.sleep(random.uniform(20, 30))

            # Check if it's the "Review your application" button or the "Continue to next step" button
            if self.is_review_button_present():
                self.click_review_button()
                self.driver.save_screenshot("contact.png")
            elif self.is_next_button_present():
                self.click_next_button()
                self.driver.save_screenshot("contact.png")
            elif self.scroll_to_submit_button():
                self.driver.save_screenshot("contact.png")
            else:
                self.dismiss_modal()
                raise Exception("Neither 'Review your application' nor 'Continue to next step' button found.")
            

        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("An unexpected error occurred while applying contact info.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while applying contact info.")
    
    def apply_home_address(self):
        try:
            # Wait for form to load
            time.sleep(random.uniform(20, 30))
            logger.info("start filling home address")
            form_element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping'))
            )
           
            time.sleep(random.uniform(20, 30))

            labels_to_search = ["Street address line 1", "City", "ZIP / Postal Code", "State"]
            time.sleep(random.uniform(20, 30))
            for label_to_search in labels_to_search:
                try:
                    input_field = self.driver.find_element(
                        By.XPATH, f'//label[contains(text(), "{label_to_search}")]/following-sibling::input'
                    )
                    if not input_field.get_attribute('value') and getattr(self, label_to_search.lower().replace(" ", "_")):
                        input_field.send_keys(getattr(self, label_to_search.lower().replace(" ", "_")))
                
                except NoSuchElementException:
                    logger.warning(f"Input field for '{label_to_search}' not found.")

            time.sleep(random.uniform(20, 30))
            self.driver.save_screenshot("homeadd.png")

            # Check if it's the "Review your application" button or the "Continue to next step" button
            if self.is_review_button_present():
                self.click_review_button()
            elif self.is_next_button_present():
                self.click_next_button()
            else:
                self.dismiss_modal()
                raise Exception("Neither 'Review your application' nor 'Continue to next step' button found.")
            self.driver.save_screenshot("homeadd.png")

        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("An unexpected error occurred while applying contact info.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while applying contact info.")

    def upload_resume(self):
        try:
            time.sleep(random.uniform(20, 30))
            # Wait for the Resume form to load
            logger.info("start filling resume file")
            WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jobs-document-upload__format-text'))
            )
            logger.info("resume form loaded")

            time.sleep(random.uniform(20, 30))
            
            # Check if any resume card is already selected
            selected_resume_card = self.driver.find_elements(By.CSS_SELECTOR, '.jobs-document-upload-redesign-card__container--selected')
            
            time.sleep(random.uniform(20, 30))

            if not selected_resume_card:
                # If no resume path is provided, select the first available resume
                resume_cards = self.driver.find_elements(By.CSS_SELECTOR, '.ui-attachment.ui-attachment--pdf')
                time.sleep(random.uniform(20, 30))

                if resume_cards:
                    # Click the first available resume card
                    resume_cards[0].click()
                    time.sleep(random.uniform(20, 30))
                else:
                    raise Exception("No resume cards found on the page.")
            else:
                # Log that a resume card is already selected (optional)
                logger.info("Resume card is already selected.")

            time.sleep(random.uniform(20, 30))

            
            time.sleep(random.uniform(20, 30))
            self.driver.save_screenshot("resume.png")
            time.sleep(random.uniform(20, 30))

            # Check if it's the "Review your application" button or the "Continue to next step" button
            if self.is_review_button_present():
                self.click_review_button()
                self.driver.save_screenshot("resume.png")
            elif self.is_next_button_present():
                self.click_next_button()
                self.driver.save_screenshot("resume.png")
            else:
                self.dismiss_modal()
                self.driver.save_screenshot("resume_failed.png")
                raise Exception("Neither 'Review your application' nor 'Continue to next step' button found.")
            

            time.sleep(random.uniform(20, 30))
            self.driver.save_screenshot('resume_filled.png')    
            time.sleep(random.uniform(20, 30))

        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("An unexpected error occurred while uploading the resume.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while uploading the resume.")
    
    def additional_questions(self):
        question_types=[]
        
        questions_to_search = [
            'years of wor kexperience',
            'years of experi ence_in',
            'salary',
            'completed Bachelor Degree',
            'proficiency in english',
            # Add more questions as needed
        ]
        

        for question_to_search in questions_to_search:
            try:
                input_field = self.driver.find_element(
                    By.XPATH, f'//label[contains(translate((), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{question_to_search.lower()}")]/following-sibling::input[@type="text"]'
                )
                if not input_field.get_attribute('value') and getattr(self, question_to_search.lower().replace(" ", "_")):
                    question_types.append(('input', question_to_search))

            except NoSuchElementException:
                try:
                    radio_legend = self.driver.find_element(By.XPATH, f'//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{question_to_search.lower()}")]/following-sibling::input[@type="text"]')
                    if radio_legend:
                        question_types.append(('radio', question_to_search))

                except NoSuchElementException:
                    try:
                        dropdown_label = self.driver.find_element(By.XPATH, f'//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{question_to_search.lower()}")]/following-sibling::input[@type="text"]')
                        if dropdown_label:
                            question_types.append(('dropdown', question_to_search))

                    except NoSuchElementException:
                        logger.warning(f"Question type for '{question_to_search}' not found.")

        return question_types

    def answer_questions_based_on_keywords(self):
        time.sleep(random.uniform(20, 30))

        # Iterate through question types and handle each one
        for question_type, question_text in self.additional_questions():
            if question_type == 'input':
                self.handle_input_question(question_text)
            elif question_type == 'radio':
                self.handle_radio_question(question_text)
            elif question_type == 'dropdown':
                self.handle_dropdown_question(question_text)
            else:
                logger.warning(f"Unknown question type for '{question_text}'")

        
        time.sleep(random.uniform(20, 30))
        self.driver.save_screenshot("contact.png")
        time.sleep(random.uniform(20, 30))

            # Check if it's the "Review your application" button or the "Continue to next step" button
        if self.is_review_button_present():
            self.click_review_button()
            self.driver.save_screenshot("add_que.png")
        elif self.is_next_button_present():
            self.click_next_button()
            self.driver.save_screenshot("add_que.png")
        else:
            self.dismiss_modal()
            self.driver.save_screenshot("add_que_failed.png")
            raise Exception("Neither 'Review your application' nor 'Continue to next step' button found.")
            
    def handle_input_question(self, question_text):
        try:
            time.sleep(random.uniform(20, 30))
            input_field = self.driver.find_element(
                By.XPATH, f'//label[contains(text(), "{question_text}")]/following-sibling::input'
                )
            input_field.send_keys(getattr(self, question_text.lower().replace(" ", "_")))

        except NoSuchElementException:
            logger.warning(f"Input field for '{question_text}' not found.")

    def handle_radio_question(self, question_text):
        try:
            time.sleep(random.uniform(20, 30))
            radio_options = self.driver.find_elements(
                By.XPATH, f'//legend[contains(text(), "{question_text}")]/following-sibling::div[contains(@class, "fb-text-selectable__option")]/input[@type="radio"]'
                )
            answer = self.determine_radio_answer(question_text, radio_options)
            time.sleep(random.uniform(20, 30))
            self.select_radio_button(radio_options, answer)

        except NoSuchElementException:
            logger.warning(f"Radio button options for '{question_text}' not found. Page structure may have changed.")

    def handle_dropdown_question(self, question_text):
        time.sleep(random.uniform(20, 30)) 
        try:
            dropdown_field = self.driver.find_element(
                By.XPATH, f'//label[contains(text(), "{question_text}")]/following-sibling::select[@data-test-text-entity-list-form-select]'
                )
            options = dropdown_field.find_elements(By.TAG_NAME, 'option')
            answer = self.determine_dropdown_answer(question_text, options)
            time.sleep(random.uniform(20, 30))
            self.select_dropdown(dropdown_field, answer)

        except NoSuchElementException:
            logger.warning(f"Dropdown options for '{question_text}' not found. Page structure may have changed.")

    def scroll_to_submit_button(self):
        try:
            # Find the "Submit application" button
            submit_button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label ='Submit application')]"))
            )

            # Scroll down to the button
            while not self.is_element_visible(submit_button):
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.DOWN)

            # Click the "Submit application" button
            submit_button.click()

            # Wait for the window to open and find the "Dismiss" button
            dismiss_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
            )

            # Click the "Dismiss" button
            dismiss_button.click()

        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("An unexpected error occurred while scrolling to and clicking the Submit application button.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while scrolling to and clicking the Submit application button.")

    def is_element_visible(self, element):
        try:
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def click_next_button(self):
        next_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step']")
        next_button.click()

    def click_review_button(self):
        review_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Review your application']")
        review_button.click()

    def is_review_button_present(self):
        try:
            self.driver.find_element(By.XPATH, "//button[@aria-label='Review your application']")
            return True
        except NoSuchElementException:
            return False

    def is_next_button_present(self):
        try:
            self.driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step']")
            return True
        except NoSuchElementException:
            return False

    def apply_easy_apply_filter(self):
        time.sleep(random.uniform(20, 30))
        try:
            # Check if the "Easy Apply" button is already enabled
            easy_apply_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Easy Apply filter.']")
            time.sleep(random.uniform(20, 30))
            
            # Check if the button has the "aria-checked" attribute set to "false"
            if easy_apply_button.get_attribute('aria-checked') == 'false':
                # Clicking the "Easy Apply" button to enable it
                easy_apply_button.click()
                time.sleep(random.uniform(20, 30))

                # Wait for the page to reload with Easy Apply jobs
                WebDriverWait(self.driver, 100).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-search-results-list"))
                )
                time.sleep(random.uniform(20, 30))
                print("Wait page to reload")
                self.driver.save_screenshot("EasyApply_button.png")
                
            else:
                print("Easy Apply button is already enabled.")
                self.driver.save_screenshot("EasyApply_button.png")
                time.sleep(random.uniform(20, 30))
            
    
        except NoSuchElementException:
            logger.error("Easy Apply button not found.")
        except (TimeoutException, WebDriverException) as te:
            logger.error(f"TimeoutException: {te}")
            raise Exception("Timed out waiting for Easy Apply jobs.")
        except Exception as e:
            logger.error(f"Exception: {e}")
            raise Exception("An unexpected error occurred while applying Easy Apply filter.")

    def filter_job(self, job_element):
        try:
            # Extract job details from the provided job_element
            job_type = job_element.find_element(By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-insight-view-model-primary').text
            job_work_type = job_element.find_element(By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-insight-view-model-secondary:nth-child(2)').text
            job_experience = job_element.find_element(By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-insight-view-model-secondary:nth-child(3)').text

            # Check if any filters are chosen
            if 'desired_job_type' not in self.parameters and 'desired_work_type' not in self.parameters and 'desired_experience' not in self.parameters:
                print("No filters chosen. Applying for the job without filtering.")
                return True

            # Check against user preferences
            if 'desired_job_type' in self.parameters and self.parameters['desired_job_type'].lower() not in job_type.lower():
                return False

            if 'desired_work_type' in self.parameters and self.parameters['desired_work_type'].lower() not in job_work_type.lower():
                return False

            if 'desired_experience' in self.parameters and self.parameters['desired_experience'].lower() not in job_experience.lower():
                return False

            return True

        except NoSuchElementException:
            # Handle the case where one of the required elements is not found
            return False
    
    def are_filters_applied(self):
        # Check if any filters are chosen
        return any(filter_param in self.parameters for filter_param in ['desired_job_type', 'desired_work_type', 'desired_experience'])

    def answer_radio_question(self, radio_element, answer):
        # Assuming 'answer' is the value to select (e.g., 'Yes' or 'No')
        radio_button = radio_element.find_element(By.XPATH, './/input[@type="radio"]')
        time.sleep(random.uniform(20, 30))
        radio_button.click()
        logger.info("radio button clicked")

    def answer_numeric_question(self, input_element, answer):
        # Assuming 'answer' is a string to be entered into the input field
        input_field = input_element.find_element(By.XPATH, './/input[@type="text"]')
        input_field.clear()
        time.sleep(random.uniform(20, 30))
        input_field.send_keys(answer)

    def answer_dropdown_question(self, select_element, answer):
        try:
            # Assuming 'answer' is the visible text of the option to select
            select = select_element.find_element(By.XPATH, './/select')
            select = Select(select)
            select.select_by_visible_text(answer)
        except NoSuchElementException:
            logger.warning(f"Option not found: {answer}")

    def check_for_search_results(self):
        """
        Check if search results are present.
        Returns True if results are found, False otherwise.
        """
        logger.info("Checking if there are results")
        
        if self.driver.find_elements(By.CSS_SELECTOR, "div.jobs-search-results-list"):
            time.sleep(random.uniform(10, 20))
            self.driver.save_screenshot('search_results.png')

            time.sleep(random.uniform(10, 20))
            self.driver.save_screenshot('search_results.png')
            logger.info("Screenshot saved!")
            return True
        
        elif self.driver.find_elements(By.CSS_SELECTOR, "div.jobs-search-no-results-banner"):
            # Handle the case where no matching jobs are found
            logger.info("No matching jobs found. Clearing filters...")
            self.clear_all_filters()
            return False
        else:
            # Handle other unexpected scenarios
            logger.warning("Unexpected scenario. Check for search results failed.")
            return False

    def get_base_search_url(self, parameters):
        remote_url = ""
        
        if parameters.get('remote'):
            remote_url = "&f_CF=f_WRA"

        level = 1
        experience_level = parameters.get('experienceLevel', [])
        experience_url = "&f_E="
        
        for level in experience_level:
                experience_url += "%2C" + str(level)
                level += 1

        distance_url = f"?distance={parameters.get('distance', 25)}"

        job_types_url = "&f_JT="
        job_types = parameters.get('experienceLevel', [])
        for key in job_types:
            if job_types[key]:
                job_types_url += "%2C" + key[0].upper()

        date_url = ""
        dates = {"all time": "", "month": "&f_TPR=r2592000", "week": "&f_TPR=r604800", "24 hours": "&f_TPR=r86400"}
        date_table = parameters.get('date', [])
        for key in date_table:
            if date_table[key]:
                date_url = dates[key]
                break

        easy_apply_url = "&f_LF=f_AL"
        
        extra_search_terms = [distance_url, remote_url, job_types_url, experience_url]
        extra_search_terms_str = ''.join(term for term in extra_search_terms if len(term) > 0) + easy_apply_url + date_url
        return f"https://www.linkedin.com/jobs/search/{extra_search_terms_str}&origin=JOBS_HOME_SEARCH_BUTTON&refresh=true"

    def avoid_lock(self):
        if self.disable_lock:
            return

        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(1.0)
        pyautogui.press('esc')  

    def logout(self):
        pass
    def close(self):
        self.driver.quit()





bot = LinkedInBot(parameters)

print("Initialized LinkedInBot")

try:
    bot.avoid_lock()
    bot.login()
    print("Login completed")
    bot.apply_filters()
    print("Started Appllying Process")
    bot.apply_to_job()

    
finally:
    bot.close()
    print("Script completed")

