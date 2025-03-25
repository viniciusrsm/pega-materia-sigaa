import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class SigaaEnroller:
    def __init__(self, codesClasses):
        load_dotenv()
        self.codesClasses = codesClasses
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        
    def run(self):
        try:
            self.driver.get("https://sigaa.unb.br/sigaa/paginaInicial.do")
            self.login()
            self.navigate_to_enrollment()
            self.enroll()
            self.confirm()
        except Exception as e:
            print(f"Error: {e}")
            
    def login(self):
        usernameInput = self.driver.find_element(By.ID, "username")
        passwordInput = self.driver.find_element(By.ID, "password")
        submitBtn = self.driver.find_element(By.NAME, "submit")
        usernameInput.send_keys(os.getenv('USER'))
        passwordInput.send_keys(os.getenv('PASSWORD'))
        submitBtn.click()
        self.driver.implicitly_wait(10)
        
    def navigate_to_enrollment(self):
        cookiesButton = self.driver.find_element(By.CSS_SELECTOR, "#sigaa-cookie-consent > button")
        menu = self.driver.find_element(By.CSS_SELECTOR, "td.ThemeOfficeMainItem:nth-child(1)")
        subMenu = self.driver.find_element(By.CSS_SELECTOR, "tr.ThemeOfficeMenuItem:nth-child(13) > td:nth-child(2)")
        enrollPageBtn = self.driver.find_element(By.CSS_SELECTOR, "#cmSubMenuID3 > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(2)")
        
        cookiesButton.click()
        menu.click()
        subMenu.click()
        enrollPageBtn.click()
        self.driver.implicitly_wait(10)
        
    def enroll(self):
        codeInput = self.driver.find_element(By.ID, "form:txtCodigo")
        codeInput.send_keys(self.codesClasses[0][0])
        codeInput.send_keys(Keys.RETURN)

        self.driver.implicitly_wait(10)
        classesTable = self.driver.find_element(By.ID, "lista-turmas-extra")
        classes = classesTable.find_elements(By.TAG_NAME, "tr")
        for cla in classes:
            if (self.codesClasses[0][1] in cla.text):
                btn = cla.find_elements(By.TAG_NAME, "a")[1]
                btn.click()
                break
        self.driver.implicitly_wait(10)
        
    def confirm(self):
        confirmTable = self.driver.find_element(By.CSS_SELECTOR, ".subFormulario > tbody:nth-child(2)")
        fields = confirmTable.find_elements(By.TAG_NAME, "tr")
        for field in fields:
            inputValue = ''
            match field.text.replace(":", ""):
                case "CPF":
                    inputValue = os.getenv('CPF')
                case "Data de Nascimento":
                    inputValue = os.getenv('BIRTH_DATE')
                case "Senha":
                    inputValue = os.getenv('PASSWORD')
            fieldInput = field.find_element(By.TAG_NAME, "input")
            fieldInput.send_keys(inputValue)
        
        confirmBtn = self.driver.find_element(By.CSS_SELECTOR, "#j_id_jsp_334536566_1\:btnConfirmar")
        confirmBtn.click()
        alert = self.driver.switch_to.alert
        alert.accept()  

if __name__ == "__main__":
    codesClasses = []
    classesCount = input("Quantas disciplinas deseja se matricular? \n")
    for i in range(int(classesCount)):
        code = input(f"Digite o código da disciplina {i+1}: \n").replace(' ', '')
        classNumber = input("Digite o número da turma dessa disciplina: \n").lstrip('0').replace(' ', '')
        if (int(classNumber) < 10): classNumber = '0' + classNumber
        codesClasses.append((code, f'Turma {classNumber}'))
    
    enroller = SigaaEnroller(codesClasses)
    enroller.run()