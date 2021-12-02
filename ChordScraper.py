from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class ChordScraper:
    def __init__(self):
        pass

    @staticmethod
    def query_cleaner(query1):
        if ',' in query1:
            query1 = query1.replace(',', '')
        if "'" in query1:
            query1 = query1.replace("'", '')
        if 'ó' in query1:
            query1 = query1.replace('ó', 'o')
        if '&' in query1:
            query1 = query1.replace("&", 'and')
        if ':' in query1:
            query1 = query1.replace(":", '')
        if '.' in query1:
            query1 = query1.replace('.', '')
        if '(' in query1:
            query1 = query1.replace('(', '')
        if ')' in query1:
            query1 = query1.replace(')', '')
        if 'ü' in query1:
            query1 = query1.replace('ü', 'u')
        if 'ğ' in query1:
            query1 = query1.replace('ğ', 'g')
        if 'ö' in query1:
            query1 = query1.replace('ö', 'o')
        if 'ç' in query1:
            query1 = query1.replace('ç', 'c')
        if 'ş' in query1:
            query1 = query1.replace('ş', 's')
        if 'ı' in query1:
            query1 = query1.replace('ı', 'i')
        query1 = query1.strip()
        query1 = query1.lower()
        return query1

    @staticmethod
    def search_string_creator(song, artist):
        song = ChordScraper.query_cleaner(song)
        if " - " in song:
            ind = song.index(" - ")
            song = song[:ind]
        if " (" in song:
            ind = song.index(" (")
            song = song[:ind]
        artist = ChordScraper.query_cleaner(artist)
        if " and" in artist:
            ind = artist.index(" and")
            artist = artist[:ind]
        ulti_search_words = []
        nsong = song.split(" ")
        nartist = artist.split(" ")
        for word in nsong:
            ulti_search_words.append(word)
        for word in nartist:
            ulti_search_words.append(word)
        search_term = ""
        for word in ulti_search_words:
            search_term += f"{word}%20"
        search_term_final = search_term[:-3:]
        return search_term_final

    @staticmethod
    def chord_entry_selector(search_term_final):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/90.0.4430.212 Safari/537.36"
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(f'user-agent={user_agent}')
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        # chrome_options.add_argument('--disable-gpu')  # is this necessary?
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        driver.get(f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_term_final}")
        try:
            WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions) \
                .until(EC.presence_of_element_located((By.CLASS_NAME, "_3uKbA")))
        except TimeoutException:
            print("Timeout Exception Occured in chord_entry_selector")
            chord_link = ""
            return driver, chord_link
        tabs_list = driver.find_elements_by_class_name("_3uKbA")
        tabs_list_only_chords = []
        time.sleep(0.3)
        for tab in tabs_list:
            try:
                WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions) \
                    .until(EC.presence_of_element_located((By.CLASS_NAME, "_2Fdo4")))
                tab_type = tab.find_element_by_class_name("_2Fdo4").text
                if "ords" in tab_type:
                    tabs_list_only_chords.append(tab)
                else:
                    pass
            except NoSuchElementException:
                pass
            except StaleElementReferenceException:
                print("StaleElementReferenceException Raised")
            except TimeoutException:
                print("Timeout Exception Occured in chord_entry_selector #2")
        tabs_list_5star = []
        tabs_list_4halfstar = []
        tabs_list_4star = []
        tabs_list_3halfstar = []
        for tab in tabs_list_only_chords:
            rating_selector = tab.find_elements_by_class_name("_1foT2")
            star_full = 0
            star_half = 0
            star_empty = 0
            for star in rating_selector:
                starclass = star.get_attribute('class')
                if 'A5Qy' in starclass:
                    star_empty += 1
                elif '3f1m' in starclass:
                    star_half += 1
                else:
                    star_full += 1
            if star_full == 5:
                tabs_list_5star.append(tab)
            elif star_full == 4 and star_half == 1:
                tabs_list_4halfstar.append(tab)
            elif star_full == 4 and star_half == 0:
                tabs_list_4star.append(tab)
            elif star_full == 3 and star_half == 1:
                tabs_list_3halfstar.append(tab)
            else:
                pass

        if len(tabs_list_5star) != 0:
            if len(tabs_list_5star) == 1:
                chord_link = tabs_list_5star[0].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
            else:
                times_rated = []
                for tab in tabs_list_5star:
                    rating_count = tab.find_element_by_class_name("zNNoF").text
                    if ',' in rating_count:
                        rating_count = rating_count.replace(",", "")
                    times_rated.append(int(rating_count))
                index_of_highest_rated = times_rated.index(max(times_rated))
                chord_link = tabs_list_5star[index_of_highest_rated].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
        elif len(tabs_list_4halfstar) != 0:
            if len(tabs_list_4halfstar) == 1:
                chord_link = tabs_list_4halfstar[0].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
            else:
                times_rated = []
                for tab in tabs_list_4halfstar:
                    rating_count = tab.find_element_by_class_name("zNNoF").text
                    if ',' in rating_count:
                        rating_count = rating_count.replace(",", "")
                    times_rated.append(int(rating_count))
                index_of_highest_rated = times_rated.index(max(times_rated))
                chord_link = tabs_list_4halfstar[index_of_highest_rated].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
        elif len(tabs_list_4star) != 0:
            if len(tabs_list_4star) == 1:
                chord_link = tabs_list_4star[0].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
            else:
                times_rated = []
                for tab in tabs_list_4star:
                    rating_count = tab.find_element_by_class_name("zNNoF").text
                    if ',' in rating_count:
                        rating_count = rating_count.replace(",", "")
                    times_rated.append(int(rating_count))
                index_of_highest_rated = times_rated.index(max(times_rated))
                chord_link = tabs_list_4star[index_of_highest_rated].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
        elif len(tabs_list_3halfstar) != 0:
            if len(tabs_list_3halfstar) == 1:
                chord_link = tabs_list_3halfstar[0].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
            else:
                times_rated = []
                for tab in tabs_list_3halfstar:
                    rating_count = tab.find_element_by_class_name("zNNoF").text
                    if ',' in rating_count:
                        rating_count = rating_count.replace(",", "")
                    times_rated.append(int(rating_count))
                index_of_highest_rated = times_rated.index(max(times_rated))
                chord_link = tabs_list_3halfstar[index_of_highest_rated].find_element_by_css_selector("a._3DU-x.JoRLr._3dYeW").get_attribute(
                    "href")
                return driver, chord_link
        else:
            print("No decent chords were found.")
            chord_link = ""
            return driver, chord_link

    @staticmethod
    def chords_retriever(driver, chordlink):
        if len(chordlink) < 2:
            html_source_text = "Sorry, no decent chords were found."
            driver.close()
        else:
            driver.get(chordlink)
            article_xpath = '/html/body/div[1]/div[2]/main/div[2]/article/div[1]/div/article/section[3]'
            html_source_text = driver.find_element_by_xpath(article_xpath).text
            driver.close()
        return html_source_text

    @staticmethod
    def get_chords(song, artist):
        search_term1 = ChordScraper.search_string_creator(song, artist)
        driver, chord_link = ChordScraper.chord_entry_selector(search_term1)
        html_source_text = ChordScraper.chords_retriever(driver, chord_link)
        retrieved_song = song
        return html_source_text, retrieved_song

