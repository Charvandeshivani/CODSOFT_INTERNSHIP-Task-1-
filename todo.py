import json
import os
import random
from datetime import datetime

# --- COLOR CONSTANTS FOR INTERACTIVE CLI ---
CLR_HEADER = "\033[95m"
CLR_BLUE = "\033[94m"
CLR_CYAN = "\033[96m"
CLR_GREEN = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_RED = "\033[91m"
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_DIM = "\033[90m"
CLR_STRIKE = "\033[9m"

# --- CONFIGURATIONS ---
PRIORITIES = {
    "H": {"label": "High", "color": CLR_RED, "icon": "🔴"},
    "M": {"label": "Medium", "color": CLR_YELLOW, "icon": "🟡"},
    "L": {"label": "Low", "color": CLR_GREEN, "icon": "🟢"},
}

QUOTES = [
    "Action is the foundational key to all success. - Pablo Picasso",
    "Focus on being productive instead of busy. - Tim Ferriss",
    "The secret of getting ahead is getting started. - Mark Twain",
    "Tomorrow becomes never. Do it today!",
    "Small progress each day adds up to big results.",
]


class TaskManager:
    """Handles advanced productivity data logic including subtasks and filtering."""

    def __init__(self, filename="tasks.json", backup_filename="backup_tasks.json"):
        self.filename = filename
        self.backup_filename = backup_filename
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Loads and structures schema fields safely."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    loaded_tasks = json.load(f)
                
                self.tasks = []
                for t in loaded_tasks:
                    if isinstance(t, dict):
                        t.setdefault("title", "Untitled Task")
                        t.setdefault("category", "General")
                        t.setdefault("notes", "")
                        t.setdefault("completed", False)
                        t.setdefault("priority", "M")
                        t.setdefault("deadline", "")
                        t.setdefault("subtasks", [])
                        t.setdefault("created_at", datetime.now().strftime("%Y-%m-%d"))
                        self.tasks.append(t)
                self.save_tasks()
            except json.JSONDecodeError:
                print(f"{CLR_RED}⚠️ Primary file corrupted. Restoring backup...{CLR_RESET}")
                self.restore_from_backup()
        else:
            self.tasks = []

    def save_tasks(self):
        """Commits states synchronously to files."""
        try:
            with open(self.filename, "w") as f:
                json.dump(self.tasks, f, indent=4)
            with open(self.backup_filename, "w") as f_b:
                json.dump(self.tasks, f_b, indent=4)
        except Exception as e:
            print(f"{CLR_RED}❌ Save failure: {e}{CLR_RESET}")

    def restore_from_backup(self):
        if os.path.exists(self.backup_filename):
            try:
                with open(self.backup_filename, "r") as f:
                    self.tasks = json.load(f)
                self.save_tasks()
            except Exception:
                self.tasks = []

    def add_task(self, title, category, priority, deadline, notes):
        task = {
            "title": title,
            "category": category if category else "General",
            "priority": priority,
            "deadline": deadline,
            "notes": notes,
            "completed": False,
            "subtasks": [],
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        self.tasks.append(task)
        self.save_tasks()

    def add_subtask(self, task_idx, subtask_title):
        if 0 <= task_idx < len(self.tasks):
            self.tasks[task_idx]["subtasks"].append({"title": subtask_title, "completed": False})
            self.save_tasks()
            return True
        return False

    def toggle_subtask(self, task_idx, sub_idx):
        if 0 <= task_idx < len(self.tasks):
            subs = self.tasks[task_idx]["subtasks"]
            if 0 <= sub_idx < len(subs):
                subs[sub_idx]["completed"] = not subs[sub_idx]["completed"]
                self.save_tasks()
                return True
        return False

    def update_task(self, index, **kwargs):
        if 0 <= index < len(self.tasks):
            for key, val in kwargs.items():
                if val is not None:
                    self.tasks[index][key] = val
            self.save_tasks()
            return True
        return False

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            removed = self.tasks.pop(index)
            self.save_tasks()
            return removed
        return None

    def mark_completed(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["completed"] = True
            # Mark all subtasks done too
            for sub in self.tasks[index]["subtasks"]:
                sub["completed"] = True
            self.save_tasks()
            return True
        return False

    def clear_completed(self):
        count = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t["completed"]]
        self.save_tasks()
        return count - len(self.tasks)

    def calculate_stats(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        pending = total - completed
        pct = (completed / total * 100) if total > 0 else 0.0
        return total, completed, pending, pct


# --- UI LAYOUT DRAWING ---

def display_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    now = datetime.now().strftime("%A, %B %d, %Y | %I:%M %p")
    quote = random.choice(QUOTES)
    print(f"{CLR_HEADER}========================================================================={CLR_RESET}")
    print(f"{CLR_CYAN}{CLR_BOLD}🚀 ADVANCED INTERACTIVE WORKSPACE HUB{CLR_RESET}")
    print(f"{CLR_BLUE}📅 {now}{CLR_RESET}")
    print(f"{CLR_HEADER}========================================================================={CLR_RESET}")
    print(f"{CLR_YELLOW}💡 \"{quote}\"{CLR_RESET}")
    print(f"{CLR_HEADER}-------------------------------------------------------------------------{CLR_RESET}\n")


def display_dashboard(manager, view_mode="ALL"):
    # Render Stats Summary
    total, completed, pending, pct = manager.calculate_stats()
    bar_len = 20
    filled = int(round(bar_len * pct / 100))
    bar = '█' * filled + '░' * (bar_len - filled)
    
    print(f"{CLR_BOLD}📊 METRICS:{CLR_RESET} Tasks: {total} | Done: {CLR_GREEN}{completed}{CLR_RESET} | Pending: {CLR_YELLOW}{pending}{CLR_RESET} [{CLR_CYAN}{bar}{CLR_RESET}] {pct:.1f}%")
    print(f"{CLR_BOLD}🔍 ACTIVE FILTER MODE:{CLR_RESET} {CLR_CYAN}{view_mode}{CLR_RESET}\n")

    # Filter/Sort Task selection
    display_list = list(enumerate(manager.tasks))
    if view_mode == "PENDING":
        display_list = [(i, t) for i, t in display_list if not t["completed"]]
    elif view_mode == "PRIORITY":
        display_list.sort(key=lambda x: ("H", "M", "L").index(x[1]["priority"]))

    if not display_list:
        print(f"   {CLR_DIM}No records matching filter settings found.{CLR_RESET}\n")
        return

    # Render Task List Items
    print(f"   {CLR_BOLD}{'ID':<4} {'Status':<5} {'Category':<11} {'Priority':<10} {'Task Title & Details':<32} {'Deadline':<10}{CLR_RESET}")
    print("   " + "-" * 74)

    for idx, task in display_list:
        is_done = task["completed"]
        status_box = f"{CLR_GREEN}[✅]{CLR_RESET}" if is_done else f"{CLR_YELLOW}[  ]{CLR_RESET}"
        
        p_info = PRIORITIES.get(task["priority"], {"label": "Medium", "color": CLR_YELLOW, "icon": "🟡"})
        p_str = f"{p_info['icon']} {p_info['color']}{p_info['label']:<6}{CLR_RESET}"
        
        # Checking Deadline Status
        dl_str = task["deadline"] if task["deadline"] else "None"
        if dl_str != "None" and not is_done:
            try:
                if datetime.strptime(dl_str, "%Y-%m-%d").date() < datetime.now().date():
                    dl_str = f"{CLR_RED}{dl_str} (⚠️ OVERDUE){CLR_RESET}"
            except ValueError:
                pass # Accept descriptive string metrics like "Today" gracefully

        title_style = f"{CLR_DIM}{CLR_STRIKE}{task['title']}{CLR_RESET}" if is_done else f"{CLR_BOLD}{task['title']}{CLR_RESET}"
        cat_str = f"[{task['category']}]"[:10]

        print(f"   {idx+1:<4} {status_box:<14} {cat_str:<11} {p_str:<22} {title_style:<32} {dl_str:<10}")
        
        # Display Notes if exists
        if task["notes"]:
            print(f"        {CLR_DIM}📝 Notes: {task['notes']}{CLR_RESET}")
            
        # Display Nested Checklist Components
        if task["subtasks"]:
            for sub_idx, sub in enumerate(task["subtasks"]):
                sub_status = f"{CLR_GREEN}☑{CLR_RESET}" if sub["completed"] else "☐"
                sub_title = f"{CLR_DIM}{CLR_STRIKE}{sub['title']}{CLR_RESET}" if sub["completed"] else sub["title"]
                print(f"        └── {sub_status} Sub-{sub_idx+1}: {sub_title}")
    print()


def get_priority():
    while True:
        p = input("   Priority (H=High, M=Medium, L=Low) [M]: ").strip().upper()
        if not p: return "M"
        if p in PRIORITIES: return p
        print(f"   {CLR_RED}❌ Select H, M, or L.{CLR_RESET}")


# --- RUNTIME MANAGER LOOP ---

def main():
    manager = TaskManager()
    filter_mode = "ALL"

    while True:
        display_header()
        display_dashboard(manager, filter_mode)

        print(f"{CLR_BOLD}⚙️  CONTROL PANEL INTERFACE:{CLR_RESET}")
        print(f"   {CLR_CYAN}[1]{CLR_RESET} Quick Add Task     {CLR_CYAN}[2]{CLR_RESET} Action Completion  {CLR_CYAN}[3]{CLR_RESET} Manage Subtasks")
        print(f"   {CLR_CYAN}[4]{CLR_RESET} Change Views/Sort  {CLR_CYAN}[5]{CLR_RESET} Edit Task Details  {CLR_CYAN}[6]{CLR_RESET} Delete Task")
        print(f"   {CLR_CYAN}[7]{CLR_RESET} Clear Completed    {CLR_CYAN}[8]{CLR_RESET} Save & Exit Workspace")
        print(f"{CLR_HEADER}-------------------------------------------------------------------------{CLR_RESET}")
        
        choice = input(f"{CLR_BOLD}👉 Choice (1-8): {CLR_RESET}").strip()

        if choice == "1":
            print(f"\n{CLR_BOLD}➕ ADD NEW WORKPLACE TASK:{CLR_RESET}")
            title = input("   Task Name: ").strip()
            if not title:
                print(f"   {CLR_RED}❌ Task name mandatory.{CLR_RESET}"); input(); continue
            cat = input("   Category/Tag (e.g., Work, College, Personal): ").strip()
            priority = get_priority()
            deadline = input("   Deadline (YYYY-MM-DD) [Optional]: ").strip()
            notes = input("   Brief Descriptive Notes: ").strip()
            
            manager.add_task(title, cat, priority, deadline, notes)
            print(f"   {CLR_GREEN}✅ Task successfully integrated!{CLR_RESET}")
            input("\nPress Enter...")

        elif choice == "2":
            print(f"\n{CLR_BOLD}✅ TOGGLE COMPLETE STATUS:{CLR_RESET}")
            try:
                idx = int(input("   Enter Task ID: ")) - 1
                if manager.mark_completed(idx):
                    print(f"   {CLR_GREEN}✨ Milestone status synced!{CLR_RESET}")
                else:
                    print(f"   {CLR_RED}❌ Out of range ID.{CLR_RESET}")
            except ValueError:
                print(f"   {CLR_RED}❌ Numeric Entry required.{CLR_RESET}")
            input("\nPress Enter...")

        elif choice == "3":
            print(f"\n{CLR_BOLD}🌿 NESTED SUBTASK MANAGEMENT:{CLR_RESET}")
            try:
                t_idx = int(input("   Target Task ID: ")) - 1
                if 0 <= t_idx < len(manager.tasks):
                    print("   [1] Add Subtask Checklist Component")
                    print("   [2] Toggle Subtask Complete Status")
                    sub_op = input("   Select Operation (1-2): ").strip()
                    
                    if sub_op == "1":
                        s_title = input("   Enter Milestone Subtask Title: ").strip()
                        if s_title: manager.add_subtask(t_idx, s_title)
                    elif sub_op == "2":
                        s_idx = int(input("   Enter Sub-ID Number: ")) - 1
                        manager.toggle_subtask(t_idx, s_idx)
                else:
                    print(f"   {CLR_RED}❌ Task ID not found.{CLR_RESET}")
            except ValueError:
                print(f"   {CLR_RED}❌ Input verification failed.{CLR_RESET}")
            input("\nPress Enter...")

        elif choice == "4":
            print(f"\n{CLR_BOLD}🔍 UPDATE RENDERING VIEWS:{CLR_RESET}")
            print("   [1] Show All Tasks")
            print("   [2] Filter Incomplete/Pending Tasks")
            print("   [3] Sort Matrix by Highest Priority Group")
            v_sel = input("   Choose View Rule (1-3): ").strip()
            if v_sel == "1": filter_mode = "ALL"
            elif v_sel == "2": filter_mode = "PENDING"
            elif v_sel == "3": filter_mode = "PRIORITY"

        elif choice == "5":
            print(f"\n{CLR_BOLD}✏️ MODIFY RUNTIME TASK META DATA:{CLR_RESET}")
            try:
                idx = int(input("   Select Task ID: ")) - 1
                if 0 <= idx < len(manager.tasks):
                    print(f"   {CLR_DIM}(Leave field blank to leave unchanged){CLR_RESET}")
                    t = input("   Update Title: ").strip() or None
                    c = input("   Update Category: ").strip() or None
                    p_change = input("   Change Priority? (y/N): ").strip().lower()
                    p = get_priority() if p_change == 'y' else None
                    d = input("   Update Deadline (YYYY-MM-DD): ").strip() or None
                    n = input("   Update Notes: ").strip() or None
                    
                    manager.update_task(idx, title=t, category=c, priority=p, deadline=d, notes=n)
                    print(f"   {CLR_GREEN}✅ Records modified accurately.{CLR_RESET}")
                else:
                    print(f"   {CLR_RED}❌ Invalid Entry ID.{CLR_RESET}")
            except ValueError:
                print(f"   {CLR_RED}❌ Numeric entry validation mismatch.{CLR_RESET}")
            input("\nPress Enter...")

        elif choice == "6":
            print(f"\n{CLR_BOLD}🗑️ ERASE TARGET LOG RECORD:{CLR_RESET}")
            try:
                idx = int(input("   Target Task ID to erase: ")) - 1
                old = manager.delete_task(idx)
                if old: print(f"   {CLR_RED}💥 Deleted '{old['title']}' permanently.{CLR_RESET}")
                else: print(f"   {CLR_RED}❌ Action bounds missing.{CLR_RESET}")
            except ValueError:
                pass
            input("\nPress Enter...")

        elif choice == "7":
            removed = manager.clear_completed()
            print(f"   🧹 Purged {removed} items from cache stack."); input()

        elif choice == "8":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n\n{CLR_HEADER}========================================================================={CLR_RESET}")
            print(f"{CLR_CYAN}{CLR_BOLD}🌟 THANK YOU FOR USING ADVANCED PRODUCTIVITY HUB!{CLR_RESET}")
            print(f"{CLR_BLUE}   All engine operations and dependencies saved natively to 'tasks.json'.{CLR_RESET}")
            print(f"   Have a structured and successful day! 💼👋🏼")
            print(f"{CLR_HEADER}========================================================================={CLR_RESET}\n\n")
            break


if __name__ == "__main__":
    main()