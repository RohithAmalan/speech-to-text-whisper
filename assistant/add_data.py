import database

def main():
    print("--- Add New Employee ---")
    
    emp_id = input("Enter ID (e.g., 1227): ").strip()
    name = input("Enter Name (e.g., Sarah Connor): ").strip()
    role = input("Enter Role (e.g., Security Chief): ").strip()
    dept = input("Enter Department (e.g., Operations): ").strip()
    
    if not all([emp_id, name, role, dept]):
        print("Error: All fields are required!")
        return

    new_employee = {
        "id": emp_id,
        "name": name,
        "role": role,
        "department": dept
    }
    
    database.add_employee(new_employee)
    print("\nDone! You can now ask the assistant about this person.")

if __name__ == "__main__":
    main()
