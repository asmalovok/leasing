import sys
from datetime import date
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from getpass import getpass
from passlib.hash import bcrypt

# Параметры подключения к базе данных PostgreSQL
db_params = {
    'dbname': 'marketplace',
    'user': 'postgres',
    'password': '1',
    'host': 'localhost',
    'port': '5432'
}

# Формируем строку подключения
DATABASE_URL = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

# Создаем экземпляр базового класса для объявления моделей
Base = declarative_base()

# Определяем модели таблиц
class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)

    def __repr__(self):
        return f'<Client(id={self.id}, name={self.name}, email={self.email}, phone={self.phone})>'

class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    color = Column(String)

    def __repr__(self):
        return f'<Car(id={self.id}, brand={self.brand}, model={self.model}, year={self.year}, color={self.color})>'

class LeasingContract(Base):
    __tablename__ = 'leasing_contracts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    car_id = Column(Integer, ForeignKey('cars.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    monthly_payment = Column(Numeric(10, 2))

    client = relationship('Client', backref='leasing_contracts')
    car = relationship('Car', backref='leasing_contracts')

    def __repr__(self):
        return f'<LeasingContract(id={self.id}, client_id={self.client_id}, car_id={self.car_id}, ' \
               f'start_date={self.start_date}, end_date={self.end_date}, monthly_payment={self.monthly_payment})>'

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    leasing_contract_id = Column(Integer, ForeignKey('leasing_contracts.id'))
    payment_date = Column(Date)
    amount = Column(Numeric(10, 2))

    leasing_contract = relationship('LeasingContract', backref='payments')

    def __repr__(self):
        return f'<Payment(id={self.id}, leasing_contract_id={self.leasing_contract_id}, ' \
               f'payment_date={self.payment_date}, amount={self.amount})>'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    is_accountant = Column(Boolean, default=False)
    is_car_manager = Column(Boolean, default=False)

    def __repr__(self):
        return f'<User(id={self.id}, username={self.username}, is_admin={self.is_admin}, ' \
               f'is_accountant={self.is_accountant}, is_car_manager={self.is_car_manager})>'

# Создаем подключение к базе данных
engine = create_engine(DATABASE_URL)

# Создаем таблицы в базе данных
Base.metadata.create_all(engine)

# Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()

# Функции для управления пользователями

def register_user(username, password, is_admin=False, is_accountant=False, is_car_manager=False):
    hashed_password = bcrypt.hash(password)
    new_user = User(username=username, password=hashed_password, is_admin=is_admin, 
                    is_accountant=is_accountant, is_car_manager=is_car_manager)
    session.add(new_user)
    session.commit()
    return new_user.id

def authenticate_user(username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and bcrypt.verify(password, user.password):
        return user
    return None

# Функции операций с базой данных

def add_client(name, email, phone):
    new_client = Client(name=name, email=email, phone=phone)
    session.add(new_client)
    session.commit()
    return new_client.id

def update_client(client_id, new_name=None, new_email=None, new_phone=None):
    client = session.query(Client).filter_by(id=client_id).first()
    if client:
        if new_name:
            client.name = new_name
        if new_email:
            client.email = new_email
        if new_phone:
            client.phone = new_phone
        session.commit()
        return True
    return False

def delete_client(client_id):
    client = session.query(Client).filter_by(id=client_id).first()
    if client:
        session.delete(client)
        session.commit()
        return True
    return False

def get_all_clients():
    clients = session.query(Client).all()
    return clients

# Функции для работы с лизинговыми операциями

def add_leasing_contract(client_id, car_id, start_date, end_date, monthly_payment):
    new_contract = LeasingContract(client_id=client_id, car_id=car_id, start_date=start_date, end_date=end_date, monthly_payment=monthly_payment)
    session.add(new_contract)
    session.commit()
    return new_contract.id

def update_leasing_contract(contract_id, new_client_id=None, new_car_id=None, new_start_date=None, new_end_date=None, new_monthly_payment=None):
    contract = session.query(LeasingContract).filter_by(id=contract_id).first()
    if contract:
        if new_client_id:
            contract.client_id = new_client_id
        if new_car_id:
            contract.car_id = new_car_id
        if new_start_date:
            contract.start_date = new_start_date
        if new_end_date:
            contract.end_date = new_end_date
        if new_monthly_payment:
            contract.monthly_payment = new_monthly_payment
        session.commit()
        return True
    return False

def delete_leasing_contract(contract_id):
    contract = session.query(LeasingContract).filter_by(id=contract_id).first()
    if contract:
        session.delete(contract)
        session.commit()
        return True
    return False

def add_payment(leasing_contract_id, payment_date, amount):
    new_payment = Payment(leasing_contract_id=leasing_contract_id, payment_date=payment_date, amount=amount)
    session.add(new_payment)
    session.commit()
    return new_payment.id

def get_all_leasing_contracts():
    contracts = session.query(LeasingContract).all()
    return contracts

# Функции для работы с автомобилями

class CarManager(Base):
    __tablename__ = 'car_managers'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_car_manager = Column(Boolean, default=True)

    def __repr__(self):
        return f'<CarManager(id={self.id}, username={self.username}, is_car_manager={self.is_car_manager})>'

def add_car_manager(username, password):
    new_manager = CarManager(username=username, password=password)
    session.add(new_manager)
    session.commit()
    return new_manager.id

def authenticate_car_manager(username, password):
    manager = session.query(CarManager).filter_by(username=username).first()
    if manager and bcrypt.verify(password, manager.password):
        return manager
    return None

def add_car(brand, model, year, color):
    new_car = Car(brand=brand, model=model, year=year, color=color)
    session.add(new_car)
    session.commit()
    return new_car.id

def update_car(car_id, new_brand=None, new_model=None, new_year=None, new_color=None):
    car = session.query(Car).filter_by(id=car_id).first()
    if car:
        if new_brand:
            car.brand = new_brand
        if new_model:
            car.model = new_model
        if new_year:
            car.year = new_year
        if new_color:
            car.color = new_color
        session.commit()
        return True
    return False

def delete_car(car_id):
    car = session.query(Car).filter_by(id=car_id).first()
    if car:
        session.delete(car)
        session.commit()
        return True
    return False

def get_all_cars():
    cars = session.query(Car).all()
    return cars

# Основной пользовательский интерфейс

def print_menu(user):
    print("\nГлавное меню:")
    print("1. Просмотреть список клиентов")
    print("2. Добавить нового клиента")
    print("3. Редактировать информацию о клиенте")
    print("4. Удалить клиента")
    print("5. Просмотреть список лизинговых контрактов")
    print("6. Добавить новый лизинговый контракт")
    print("7. Редактировать лизинговый контракт")
    print("8. Удалить лизинговый контракт")
    print("9. Просмотреть список автомобилей")
    print("10. Добавить новый автомобиль")
    if user.is_car_manager:
        print("11. Просмотреть список менеджеров по поставке машин")
        print("12. Добавить нового менеджера по поставке машин")
    print("0. Выйти из программы")

def main():
    print("Добро пожаловать в систему управления лизинговыми операциями!")

    # Добавляем администратора, если его нет
    admin = session.query(User).filter_by(username='admin').first()
    if not admin:
        print("\nСоздание первого администратора:")
        admin_password = getpass("Введите пароль для администратора: ")
        register_user('admin', admin_password, is_admin=True)
        print("Первый администратор успешно создан!")

    # Аутентификация пользователя
    authenticated_user = None
    while not authenticated_user:
        username = input("\nВведите имя пользователя: ")
        password = getpass("Введите пароль: ")
        authenticated_user = authenticate_user(username, password)
        if not authenticated_user:
            print("Неправильное имя пользователя или пароль. Попробуйте снова.")

    print(f"\nДобро пожаловать, {authenticated_user.username}!")

    while True:
        print_menu(authenticated_user)
        choice = input("\nВыберите действие: ")

        if choice == '1':
            clients = get_all_clients()
            if clients:
                print("\nСписок клиентов:")
                for client in clients:
                    print(client)
            else:
                print("\nНет клиентов для отображения.")

        elif choice == '2':
            name = input("Введите имя нового клиента: ")
            email = input("Введите email нового клиента: ")
            phone = input("Введите телефон нового клиента: ")
            client_id = add_client(name, email, phone)
            print(f"Новый клиент добавлен с ID: {client_id}")

        elif choice == '3':
            client_id = input("Введите ID клиента для редактирования: ")
            new_name = input("Введите новое имя клиента (оставьте пустым, если не хотите менять): ").strip()
            new_email = input("Введите новый email клиента (оставьте пустым, если не хотите менять): ").strip()
            new_phone = input("Введите новый телефон клиента (оставьте пустым, если не хотите менять): ").strip()
            if update_client(client_id, new_name, new_email, new_phone):
                print(f"Информация о клиенте с ID {client_id} успешно обновлена.")
            else:
                print(f"Клиент с ID {client_id} не найден.")

        elif choice == '4':
            client_id = input("Введите ID клиента для удаления: ")
            if delete_client(client_id):
                print(f"Клиент с ID {client_id} успешно удален.")
            else:
                print(f"Клиент с ID {client_id} не найден.")

        elif choice == '5':
            contracts = get_all_leasing_contracts()
            if contracts:
                print("\nСписок лизинговых контрактов:")
                for contract in contracts:
                    print(contract)
            else:
                print("\nНет лизинговых контрактов для отображения.")

        elif choice == '6':
            client_id = input("Введите ID клиента для нового лизингового контракта: ")
            car_id = input("Введите ID автомобиля для нового лизингового контракта: ")
            start_date = input("Введите дату начала контракта (гггг-мм-дд): ")
            end_date = input("Введите дату окончания контракта (гггг-мм-дд): ")
            monthly_payment = input("Введите ежемесячный платеж: ")
            contract_id = add_leasing_contract(client_id, car_id, start_date, end_date, monthly_payment)
            print(f"Новый лизинговый контракт добавлен с ID: {contract_id}")

        elif choice == '7':
            contract_id = input("Введите ID лизингового контракта для редактирования: ")
            new_client_id = input("Введите новый ID клиента (оставьте пустым, если не хотите менять): ").strip()
            new_car_id = input("Введите новый ID автомобиля (оставьте пустым, если не хотите менять): ").strip()
            new_start_date = input("Введите новую дату начала контракта (гггг-мм-дд, оставьте пустым, если не хотите менять): ").strip()
            new_end_date = input("Введите новую дату окончания контракта (гггг-мм-дд, оставьте пустым, если не хотите менять): ").strip()
            new_monthly_payment = input("Введите новый ежемесячный платеж (оставьте пустым, если не хотите менять): ").strip()
            if update_leasing_contract(contract_id, new_client_id, new_car_id, new_start_date, new_end_date, new_monthly_payment):
                print(f"Лизинговый контракт с ID {contract_id} успешно обновлен.")
            else:
                print(f"Лизинговый контракт с ID {contract_id} не найден.")

        elif choice == '8':
            contract_id = input("Введите ID лизингового контракта для удаления: ")
            if delete_leasing_contract(contract_id):
                print(f"Лизинговый контракт с ID {contract_id} успешно удален.")
            else:
                print(f"Лизинговый контракт с ID {contract_id} не найден.")

        elif choice == '9':
            cars = get_all_cars()
            if cars:
                print("\nСписок автомобилей:")
                for car in cars:
                    print(car)
            else:
                print("\nНет автомобилей для отображения.")

        elif choice == '10':
            brand = input("Введите марку нового автомобиля: ")
            model = input("Введите модель нового автомобиля: ")
            year = input("Введите год выпуска нового автомобиля: ")
            color = input("Введите цвет нового автомобиля: ")
            car_id = add_car(brand, model, year, color)
            print(f"Новый автомобиль добавлен с ID: {car_id}")

        elif choice == '11' and authenticated_user.is_car_manager:
            managers = session.query(CarManager).all()
            if managers:
                print("\nСписок менеджеров по поставке машин:")
                for manager in managers:
                    print(manager)
            else:
                print("\nНет менеджеров по поставке машин для отображения.")

        elif choice == '12' and authenticated_user.is_car_manager:
            manager_username = input("Введите имя пользователя нового менеджера по поставке машин: ")
            manager_password = getpass("Введите пароль для нового менеджера по поставке машин: ")
            manager_id = add_car_manager(manager_username, manager_password)
            print(f"Новый менеджер по поставке машин добавлен с ID: {manager_id}")

        elif choice == '0':
            print("Выход из программы...")
            break

        else:
            print("Неверный ввод. Пожалуйста, выберите один из предложенных вариантов.")

    # Закрываем сессию после завершения работы с программой
    session.close()

if __name__ == "__main__":
    main()
