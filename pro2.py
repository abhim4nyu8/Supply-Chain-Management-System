import json
import time
import hashlib
import pyqrcode
import png

# Define a class for representing a Transaction
class Transaction:
    def __init__(self, order_id, product_name, status, manufacturer=None, distributor=None, client=None, timestamp=time.ctime()):
        self.product_name = product_name
        self.timestamp = timestamp
        self.manufacturer = manufacturer
        self.distributor = distributor
        self.client = client
        self.status = status
        self.order_id = order_id
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Calculate a hash for the transaction using orderId and timestamp
        return hashlib.sha256(json.dumps({"orderId": self.order_id, "time": self.timestamp}).encode('utf-8')).hexdigest()

    def __str__(self):
        return str(self.__dict__)

# Define a class for representing a Block
class Block:
    def __init__(self, timestamp, transactions, prev_hash, nonce, difficulty):
        self.timestamp = timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.difficulty = difficulty
        self.hash = self.calculate_hash()
        self.merkle_root = self.calculate_merkle_root()

    def calculate_hash(self):
        # Calculate a hash for the block using transaction hashes, timestamp, previous hash, and nonce
        sha = hashlib.sha256("".join([str(i.hash) for i in self.transactions]).encode('utf-8'))
        sha.update(str(self.timestamp).encode('utf-8') + str(self.prev_hash).encode('utf-8') + str(self.nonce).encode('utf-8'))
        return sha.hexdigest()

    def mine(self):
        # Mine the block by finding a hash that meets the required difficulty
        while self.hash[:self.difficulty] != '0' * self.difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f'Block mined: {self.hash}')

    def calculate_merkle_root(self):
        # Calculate the Merkle root of transactions in the block
        transaction_hashes = [tx.hash for tx in self.transactions]
        if len(transaction_hashes) % 2 != 0:
            transaction_hashes.append(transaction_hashes[-1])
        while len(transaction_hashes) > 1:
            new_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                new_hashes.append(hashlib.sha256((transaction_hashes[i] + transaction_hashes[i+1]).encode('utf-8')).hexdigest())
            transaction_hashes = new_hashes
            if len(transaction_hashes) % 2 != 0 and len(transaction_hashes) != 1:
                transaction_hashes.append(transaction_hashes[-1])
        return transaction_hashes[0]

    def __str__(self):
        # Convert the block object to a string for easy printing
        x = self.__dict__
        y = x.copy()
        y["transactions"] = [str(i) for i in self.transactions]
        return str(y)

# Define a class for representing a Blockchain
class Blockchain:
    def __init__(self, difficulty):
        self.chain = []
        self.difficulty = difficulty
        self.pending_transactions = []

    def generate_qr_code(self, order_id):
        # Generate a QR code for a specific order ID and its details
        for i in range(len(self.chain) - 1, -1, -1):
            for j in range(len(self.chain[i].transactions) - 1, -1, -1):
                if self.chain[i].transactions[j].order_id == int(order_id):
                    s = {
                        "OrderID": order_id,
                        "Timestamp": self.chain[i].transactions[j].timestamp,
                        "ProductId": self.chain[i].transactions[j].product_name,
                        "Client": self.chain[i].transactions[j].client.name,
                        "Status": self.chain[i].transactions[j].status
                    }
                    s["distributor"] = "None" if self.chain[i].transactions[j].distributor is None else self.chain[i].transactions[j].distributor.name
                    qr = pyqrcode.create(str(s))
                    qr.png('found.png', scale=7)
                    return
        print("Order not found")

    def add_transaction(self, transaction):
        # Add a transaction to the list of pending transactions
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        # Mine a new block with pending transactions
        if len(self.chain) == 0:
            prev_hash = "0"
        else:
            prev_hash = self.chain[-1].hash
        block = Block(time.time(), self.pending_transactions, prev_hash, 0, self.difficulty)
        block.mine()
        self.chain.append(block)
        self.pending_transactions = []

    def print_blockchain(self):
        # Print the entire blockchain
        for block in self.chain:
            print("Block ", block, "\n")

    def __str__(self):
        return str(self.__dict__)
   


        # Transfer the valid transactions to confirmed_transactions
        for tx in transactions_to_confirm:
            self.clients[str(tx.client_id)].balance -= tx.amount  # Deducting the transaction amount from the client
            self.confirmed_transactions.append(tx)
            self.pending_transactions.remove(tx)
            print(f"Transaction for Product {tx.product_id} is verified and added to confirmed transactions!")

        # Remove invalid transactions
        for tx in transactions_to_remove:
            self.pending_transactions.remove(tx)

# Define a class for representing a Client
class Client:
    def __init__(self, security_deposit):
        self.name = input("Enter name: ")
        self.security_deposit = security_deposit
        CLIENT_LIST[self.name] = self
        self.orders = {}

    def confirm_delivery(self):
        # Confirm the delivery of an order
        order_list = list(enumerate(self.orders))
        print(*order_list, sep="\n")
        order_id_index = int(input("Enter order ID index: "))
        if self.orders[order_list[order_id_index][1]][1] != 'unassigned':
            BLOCK_CHAIN.add_transaction(Transaction(order_list[order_id_index][1], self.orders[order_list[order_id_index][1]][0], "DELIVERED", None, self.orders[order_list[order_id_index][1]][1], self))
            del (self.orders[order_list[order_id_index][1]])
        else:
            print("Delivery not possible")

    def user_menu(self):
        # Display the user menu for clients
        choice = 1
        while choice != 4:
            print("1. Place orders", "2. Confirm Delivery", "3. Show orders", "4. Log Out", sep="\n")
            choice = int(input("Enter Choice: "))
            if choice == 1:
                order = MANUFACTURER.add_order(self)
                if order:
                    self.orders[order[0]] = order[1:]
            elif choice == 2 and len(self.orders):
                self.confirm_delivery()
            elif choice == 3:
                print(self.orders, sep="\n")

    def __str__(self):
        return f'Client [name: {self.name}]'

# Define a class for representing a Distributor
class Distributor:
    def __init__(self, security_deposit):
        self.name = input("Enter name: ")
        self.security_deposit = security_deposit
        self.free = True
        self.current_order = None
        DISTRIBUTOR_LIST[self.name] = self

    def send_order(self):
        # Send an order to a client
        print("Order sent")
        BLOCK_CHAIN.add_transaction(Transaction(self.current_order[0], self.current_order[1], "Transit to Client", None, self, self.current_order[2]))
        (self.current_order[2]).orders[self.current_order[0]][1] = self
        self.current_order = None
        self.free = True

    def user_menu(self):
        # Display the user menu for distributors
        choice = 1
        while choice != 3:
            print("1. Get Orders", "2. Send Order", "3. Log Out", sep="\n")
            choice = int(input("Enter Choice: "))
            if choice == 1 and self.free:
                self.free, self.current_order = MANUFACTURER.get_order(self)
            elif choice == 2 and not self.free:
                self.send_order()
            elif choice == 1:
                print("Cannot take more orders")
            elif choice == 2:
                print("No order taken")

    def __str__(self):
        return f'Distributor [name: {self.name}]'

# Define a class for representing a Manufacturer
class Manufacturer:
    def __init__(self):
        self.products = {'chips': ["chips", 10], 'biscuit': ["biscuit", 10]}
        self.orders = []

    def get_order(self, distributor):
        # Get an order from a distributor
        for i, x in enumerate(self.orders):
            print(i, x)
        choice = int(input("Enter choice: "))
        order = list(enumerate(self.orders))[choice][1]
        if order[1][1] <= distributor.security_deposit:
            BLOCK_CHAIN.add_transaction(
                Transaction(order[0], order[3], "Transit to distributor", 1, distributor, order[2]))
            self.orders.pop(self.orders.index(order))
            return False, (order[0], order[3], order[2])
        else:
            print("Not enough money")
            return True, None

    def add_order(self, client):
        # Add an order to the list of client orders
        product_list = list(enumerate(self.products))
        c = 0
        for i in self.products:
            print(c, self.products[i][0], self.products[i][1])
            c += 1
        product_index = int(input("Enter Index: "))
        product_index = product_list[product_index][1]
        if client.security_deposit >= self.products[product_index][1]:
            global ORDER_COUNT
            order_id = ORDER_COUNT
            ORDER_COUNT += 1
            BLOCK_CHAIN.add_transaction(Transaction(order_id, product_index, "ORDERED By Client", 1, None, client))
            self.orders.append([order_id, self.products[product_index], client, product_index])
            return list([order_id, product_index, "unassigned"])
        else:
            print("Not enough money")
            return None

    def __str__(self):
        return f'Manufacturer [name: {self.name}]'

# Main menu for the program
def main_menu():
    print("1. Create User")
    print("2. Log-In")
    print("3. Mine Block")
    print("4. Print BlockChain")
    print("5. Make QR Code using Product Order ID")
    print("7.verify")
    print("6. Exit")

    choice = int(input("Enter Choice: "))
    return choice

# Function to create a new user (either Distributor or Client)
def create_user():
    print("Select User Type:")
    print("1. Distributor")
    print("2. Client")
    choice = int(input("Enter Choice: "))
    if choice == 1:
        distributor = Distributor(100)
        DISTRIBUTOR_LIST[distributor.name] = distributor
    elif choice == 2:
        client = Client(100)
        CLIENT_LIST[client.name] = client

# Function for user login
def login():
    print("Select User Type:")
    print("1. Distributor")
    print("2. Client")
    print("3. Exit")
    choice = int(input("Enter Your Choice: "))
    if choice == 1:
        name = input("Enter distributor Name: ")
        if name in DISTRIBUTOR_LIST:
            DISTRIBUTOR_LIST[name].user_menu()
        else:
            print("No distributor with this name.")
    elif choice == 2:
        name = input("Enter Client Name: ")
        if name in CLIENT_LIST:
            CLIENT_LIST[name].user_menu()
        else:
            print("No client with this name.")
    elif choice == 3:
        return
    login()

# Main loop of the program
def main_loop():
    choice = None
    while choice != 6:
        choice = main_menu()
        if choice == 1:
            create_user()
        elif choice == 2:
            login()
        elif choice == 3:
            BLOCK_CHAIN.mine_pending_transactions()
        elif choice == 4:
            BLOCK_CHAIN.print_blockchain()
        elif choice == 5:
            BLOCK_CHAIN.generate_qr_code(input("Order ID: "))
        elif choice == 7:
            BLOCK_CHAIN.verify_transactions()
            print("Product received")

# Initialize global variables and start the main loop
DISTRIBUTOR_LIST = {}
CLIENT_LIST = {}
BLOCK_CHAIN = Blockchain(1)
MANUFACTURER = Manufacturer()
ORDER_COUNT = 1
main_loop()
