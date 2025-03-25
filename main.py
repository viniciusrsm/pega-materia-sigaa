import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class SigaaEnroller:
    def __init__(self, coursesCodes: list[(str, str)]):
        load_dotenv()
        self.coursesCodes = coursesCodes
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def run(self):
        try:
            print("Inicializando a aplicação...")
            self.driver.get("https://sigaa.unb.br/sigaa/paginaInicial.do")
            self.login()
            self.navigate_to_enrollment()

            c = 0
            while True:
                code = coursesCodes[c][0]
                classNum = coursesCodes[c][1]

                enrollSuccess = self.enroll(code, classNum)
                if (enrollSuccess):
                    confirmSuccess = self.confirm(c, code)
                    if not (confirmSuccess):
                        break
                    
                if (len(self.coursesCodes) != 0): c = (c+1) % len(self.coursesCodes)
                else: break

        except Exception as e:
            print(f"Erro: {e}")
            
    def login(self):
        self.driver.implicitly_wait(10)
        usernameInput = self.driver.find_element(By.ID, "username")
        passwordInput = self.driver.find_element(By.ID, "password")
        submitBtn = self.driver.find_element(By.NAME, "submit")

        usernameInput.send_keys(os.getenv('USER'))
        passwordInput.send_keys(os.getenv('PASSWORD'))
        submitBtn.click()
        
    def navigate_to_enrollment(self):
        self.driver.implicitly_wait(10)
        cookiesButton = self.driver.find_element(By.CSS_SELECTOR, "#sigaa-cookie-consent > button")
        menu = self.driver.find_element(By.CSS_SELECTOR, "td.ThemeOfficeMainItem:nth-child(1)")
        subMenu = self.driver.find_element(By.CSS_SELECTOR, "tr.ThemeOfficeMenuItem:nth-child(13) > td:nth-child(2)")
        enrollPageBtn = self.driver.find_element(By.CSS_SELECTOR, "#cmSubMenuID3 > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(2)")
        
        cookiesButton.click()
        menu.click()
        subMenu.click()
        enrollPageBtn.click()
        
        
    def enroll(self, code, classNumber):
        print(f"Procurando a disciplina {code}...")
        self.driver.implicitly_wait(10)
        codeInput = self.driver.find_element(By.ID, "form:txtCodigo")
        codeInput.clear()
        codeInput.send_keys(code)
        codeInput.send_keys(Keys.RETURN)

        self.driver.implicitly_wait(10)
        self.driver.find_element(By.ID, "form")

        try:
            classesTable = self.driver.find_element(By.ID, "lista-turmas-extra")
        except:
            return False
        
        classes = classesTable.find_elements(By.TAG_NAME, "tr")
        for cla in classes:
            if (classNumber in cla.text):
                btn = cla.find_elements(By.TAG_NAME, "a")[1]
                btn.click()
                break

        return True

    def confirm(self, arrIndex, code):
        self.driver.implicitly_wait(10)
        confirmTable = self.driver.find_element(By.XPATH, '//*[@id="j_id_jsp_334536566_1"]/table[2]/tbody/tr[3]/td/div/div/table/tbody')

        fields = confirmTable.find_elements(By.XPATH, "./child::*")[2:]
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
        
        confirmBtn = self.driver.find_element(By.XPATH, '//*[@id="j_id_jsp_334536566_1:btnConfirmar"]')
        confirmBtn.click()
        alert = self.driver.switch_to.alert
        alert.accept()

        try:
            self.driver.implicitly_wait(30)
            self.driver.find_element(By.XPATH, '//*[@id="j_id_jsp_334536566_1"]/table[2]/tbody/tr[3]/td/div/div/table')
        except:
            print("Suas informações pessoais estão incorretas!")
            return False
        finally:
            self.coursesCodes.pop(arrIndex)
            print(f"Cadastrado na disciplina {code}.")

            returnBtn = self.driver.find_element(By.XPATH, '//*[@id="j_id_jsp_334536566_1:btnRealizarNovaMatricula"]')
            returnBtn.click()

            return True

if __name__ == "__main__":
    coursesCodes = []
    coursesCount = input("Quantas disciplinas deseja se matricular? \n")
    for i in range(int(coursesCount)):
        code = input(f"Digite o código da disciplina {i+1}: \n").replace(' ', '')
        classNumber = input("Digite o número da turma dessa disciplina: \n").lstrip('0').replace(' ', '')
        if (int(classNumber) < 10): classNumber = '0' + classNumber
        coursesCodes.append((code, f'Turma {classNumber}'))
    
    enroller = SigaaEnroller(coursesCodes)
    enroller.run()