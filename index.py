import os
import subprocess
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import re


class GitHubPusherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("🚀 GitHub Project Manager")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # HISTORY
        self.history = set()
        self.load_history()

        # CONTROL FLAG
        self.stop_requested = False

        # SAVED FOLDERS
        self.saved_folders = []
        self.load_saved_folders()

        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================================
        # SIDEBAR
        # ================================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Sidebar Title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="📁 Menu",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Menu Buttons
        self.upload_button = ctk.CTkButton(
            self.sidebar,
            text="🚀 Upload Projects",
            command=self.show_upload_page,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.upload_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.delete_button = ctk.CTkButton(
            self.sidebar,
            text="🗑 Delete Repos",
            command=self.show_delete_page,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="darkred",
            hover_color="#8B0000"
        )
        self.delete_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Separator
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray")
        separator.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # App Info
        self.info_label = ctk.CTkLabel(
            self.sidebar,
            text="GitHub Manager\nv1.1 (Org Support)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.info_label.grid(row=5, column=0, padx=20, pady=(0, 20))

        # ================================
        # MAIN CONTENT AREA
        # ================================
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Create pages
        self.create_upload_page()
        self.create_delete_page()

        # Show upload page by default
        self.show_upload_page()

        # FLAG UNTUK USERNAME/TOKEN SALAH
        self.invalid_credentials = False

    # ================================
    # PAGE MANAGEMENT
    # ================================
    def show_upload_page(self):
        """Show upload projects page"""
        self.delete_page.grid_remove()
        self.upload_page.grid()
        
        # Update button colors
        self.upload_button.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.delete_button.configure(fg_color="darkred")

    def show_delete_page(self):
        """Show delete repositories page"""
        self.upload_page.grid_remove()
        self.delete_page.grid()
        
        # Update button colors
        self.upload_button.configure(fg_color="gray")
        self.delete_button.configure(fg_color="darkred", hover_color="#8B0000")
        
        # Load repos when opening delete page
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()
        
        if username and token:
            self.load_repos()
        else:
            messagebox.showwarning("Warning", "Please enter username and token first!")
            self.show_upload_page()

    # ================================
    # UPLOAD PAGE
    # ================================
    def create_upload_page(self):
        """Create upload projects page"""
        self.upload_page = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.upload_page.grid(row=0, column=0, sticky="nsew")
        self.upload_page.grid_columnconfigure(0, weight=1)
        self.upload_page.grid_rowconfigure(6, weight=1)

        # TITLE
        title_label = ctk.CTkLabel(
            self.upload_page, text="🚀 Upload Projects to GitHub",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=20, sticky="n")

        # CREDENTIALS FRAME
        creds_frame = ctk.CTkFrame(self.upload_page)
        creds_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        creds_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(creds_frame, text="👤 Username:").grid(
            row=0, column=0, padx=10, pady=10)
        self.username_entry = ctk.CTkEntry(
            creds_frame, placeholder_text="Enter GitHub Username")
        self.username_entry.grid(
            row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(creds_frame, text="🔐 Token:").grid(
            row=1, column=0, padx=10, pady=10)
        self.token_entry = ctk.CTkEntry(
            creds_frame, show="*", placeholder_text="Enter Personal Access Token")
        self.token_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # ORGANIZATION FRAME
        org_frame = ctk.CTkFrame(self.upload_page)
        org_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        org_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(org_frame, text="🏢 Target:").grid(
            row=0, column=0, padx=10, pady=10)
        
        # Dropdown untuk pilih user atau org
        self.target_type_var = ctk.StringVar(value="User Account")
        self.target_type_menu = ctk.CTkOptionMenu(
            org_frame,
            values=["User Account", "Organization"],
            variable=self.target_type_var,
            command=self.on_target_type_change
        )
        self.target_type_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Entry untuk organization name (hidden by default)
        ctk.CTkLabel(org_frame, text="🏢 Org Name:").grid(
            row=1, column=0, padx=10, pady=10)
        self.org_entry = ctk.CTkEntry(
            org_frame, placeholder_text="Enter Organization Name (optional)")
        self.org_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.org_entry.grid_remove()  # Hide by default

        # Button to load organizations
        self.load_orgs_button = ctk.CTkButton(
            org_frame, text="📋 Load My Orgs", command=self.load_organizations, width=120)
        self.load_orgs_button.grid(row=1, column=2, padx=10, pady=10)
        self.load_orgs_button.grid_remove()  # Hide by default

        # Dropdown untuk pilih org
        self.org_dropdown = ctk.CTkOptionMenu(
            org_frame,
            values=["No organizations"],
            command=self.on_org_selected
        )
        self.org_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.org_dropdown.grid_remove()  # Hide by default

        # FOLDER FRAME
        folder_frame = ctk.CTkFrame(self.upload_page)
        folder_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        folder_frame.grid_columnconfigure(1, weight=1)

        self.folder_label = ctk.CTkLabel(
            folder_frame, text="📂 No folder selected", anchor="w")
        self.folder_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.folder_button = ctk.CTkButton(
            folder_frame, text="Select Folder", command=self.select_folder)
        self.folder_button.grid(row=0, column=1, padx=10, pady=10)

        # Save & Load Folder Buttons
        self.save_folder_button = ctk.CTkButton(
            folder_frame, text="💾 Save This Folder", command=self.save_current_folder)
        self.save_folder_button.grid(
            row=1, column=0, padx=10, pady=5, sticky="w")

        self.folder_optionmenu = ctk.CTkOptionMenu(
            folder_frame, values=["No saved folders"], command=self.select_saved_folder, 
            width=300, anchor="center", dynamic_resizing=False
        )
        self.folder_optionmenu.grid(
            row=1, column=1, padx=10, pady=5, sticky="ew")
        self.update_folder_dropdown()

        # CHECKBOX urut tahun
        self.sort_by_year_var = ctk.BooleanVar(value=False)
        self.sort_checkbox = ctk.CTkCheckBox(
            folder_frame,
            text="Urutkan berdasarkan tahun",
            variable=self.sort_by_year_var
        )
        self.sort_checkbox.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # CHECKBOX replace spasi dengan dash
        self.replace_space_var = ctk.BooleanVar(value=False)
        self.replace_space_checkbox = ctk.CTkCheckBox(
            folder_frame,
            text="Ubah spasi menjadi \"-\"",
            variable=self.replace_space_var
        )
        self.replace_space_checkbox.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # VISIBILITY FRAME (Private/Public)
        visibility_frame = ctk.CTkFrame(folder_frame)
        visibility_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(visibility_frame, text="🔒 Repository Visibility:").pack(side="left", padx=(10, 5))
        
        self.visibility_var = ctk.StringVar(value="public")
        self.public_radio = ctk.CTkRadioButton(
            visibility_frame,
            text="🌐 Public",
            variable=self.visibility_var,
            value="public"
        )
        self.public_radio.pack(side="left", padx=10)
        
        self.private_radio = ctk.CTkRadioButton(
            visibility_frame,
            text="🔒 Private",
            variable=self.visibility_var,
            value="private"
        )
        self.private_radio.pack(side="left", padx=10)

        # BUTTONS (Push + Stop + Clear Logs)
        buttons_frame = ctk.CTkFrame(self.upload_page)
        buttons_frame.grid(row=4, column=0, pady=20)

        self.push_button = ctk.CTkButton(
            buttons_frame, text="🚀 Scan and Push Projects", command=self.scan_and_push)
        self.push_button.grid(row=0, column=0, padx=10)

        self.stop_button = ctk.CTkButton(
            buttons_frame, text="⏹ Stop Push", fg_color="red",
            command=self.stop_push)
        self.stop_button.grid(row=0, column=1, padx=10)

        self.clear_log_button = ctk.CTkButton(
            buttons_frame, text="🗑 Clear Logs", fg_color="orange",
            command=self.clear_logs)
        self.clear_log_button.grid(row=0, column=2, padx=10)

        # PROGRESS BAR
        self.progress = ctk.CTkProgressBar(self.upload_page, width=600)
        self.progress.set(0)
        self.progress.grid(row=5, column=0, pady=10)

        # LOG FRAME
        log_frame = ctk.CTkFrame(self.upload_page)
        log_frame.grid(row=6, column=0, padx=20, pady=10, sticky="nsew")

        ctk.CTkLabel(log_frame, text="📜 Logs").pack(
            anchor="w", padx=10, pady=5)
        self.log_text = ctk.CTkTextbox(log_frame, height=250)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    def on_target_type_change(self, choice):
        """Handle target type change"""
        if choice == "Organization":
            self.org_entry.grid()
            self.load_orgs_button.grid()
            self.org_dropdown.grid()
            self.log("🏢 Organization mode enabled")
        else:
            self.org_entry.grid_remove()
            self.load_orgs_button.grid_remove()
            self.org_dropdown.grid_remove()
            self.log("👤 User account mode enabled")

    def load_organizations(self):
        """Load user's organizations from GitHub"""
        token = self.token_entry.get().strip()
        
        if not token:
            messagebox.showerror("Error", "Please enter token first!")
            return
        
        self.log("🔄 Loading organizations...")
        
        try:
            url = "https://api.github.com/user/orgs"
            req = Request(url)
            req.add_header("Authorization", f"token {token}")
            req.add_header("Accept", "application/vnd.github.v3+json")
            
            response = urlopen(req)
            orgs = json.loads(response.read().decode())
            
            if not orgs:
                self.log("⚠️ No organizations found")
                self.org_dropdown.configure(values=["No organizations"])
                return
            
            org_names = [org['login'] for org in orgs]
            self.org_dropdown.configure(values=org_names)
            self.log(f"✅ Loaded {len(org_names)} organizations")
            
        except HTTPError as e:
            if e.code == 401:
                self.log("❌ Invalid token!")
                messagebox.showerror("Error", "Invalid token!")
            else:
                self.log(f"❌ Error loading organizations: {e}")
        except Exception as e:
            self.log(f"❌ Error: {e}")

    def on_org_selected(self, org_name):
        """Handle organization selection"""
        if org_name != "No organizations":
            self.org_entry.delete(0, 'end')
            self.org_entry.insert(0, org_name)
            self.log(f"🏢 Selected organization: {org_name}")

    # ================================
    # DELETE PAGE
    # ================================
    def create_delete_page(self):
        """Create delete repositories page"""
        self.delete_page = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.delete_page.grid(row=0, column=0, sticky="nsew")
        self.delete_page.grid_columnconfigure(0, weight=1)
        self.delete_page.grid_rowconfigure(2, weight=1)

        # TITLE
        self.delete_title_label = ctk.CTkLabel(
            self.delete_page,
            text="🗑 Delete GitHub Repositories",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.delete_title_label.grid(row=0, column=0, pady=20, sticky="n")

        # SEARCH & FILTER FRAME
        search_frame = ctk.CTkFrame(self.delete_page)
        search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="🔍 Search:").grid(
            row=0, column=0, padx=10, pady=10)
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Type to filter repositories...")
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_repos)

        self.refresh_repos_btn = ctk.CTkButton(
            search_frame, text="🔄 Refresh", command=self.load_repos, width=100)
        self.refresh_repos_btn.grid(row=0, column=2, padx=10, pady=10)

        # REPOSITORIES FRAME
        repos_frame = ctk.CTkFrame(self.delete_page)
        repos_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        repos_frame.grid_columnconfigure(0, weight=1)
        repos_frame.grid_rowconfigure(0, weight=1)

        # Scrollable frame for checkboxes
        self.scrollable_frame = ctk.CTkScrollableFrame(repos_frame)
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # BUTTONS FRAME
        buttons_frame = ctk.CTkFrame(self.delete_page)
        buttons_frame.grid(row=3, column=0, pady=20)

        self.select_all_btn = ctk.CTkButton(
            buttons_frame, text="☑ Select All", command=self.select_all, width=120)
        self.select_all_btn.grid(row=0, column=0, padx=10)

        self.deselect_all_btn = ctk.CTkButton(
            buttons_frame, text="☐ Deselect All", command=self.deselect_all, width=120)
        self.deselect_all_btn.grid(row=0, column=1, padx=10)

        self.delete_selected_btn = ctk.CTkButton(
            buttons_frame, text="🗑 Delete Selected", fg_color="darkred",
            command=self.delete_selected, width=150)
        self.delete_selected_btn.grid(row=0, column=2, padx=10)

        # Storage for checkboxes
        self.repo_checkboxes = {}
        self.all_repos = []

    # ================================
    # DELETE PAGE FUNCTIONS
    # ================================
    def load_repos(self):
        """Load all repositories from GitHub"""
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()

        if not username or not token:
            messagebox.showerror("Error", "Please enter username and token first!")
            return

        # Clear existing checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.repo_checkboxes.clear()

        # Show loading
        loading_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="⏳ Loading repositories...",
            font=ctk.CTkFont(size=14)
        )
        loading_label.grid(row=0, column=0, pady=20)
        self.update()

        try:
            # Fetch all pages of repositories
            all_repos = []
            page = 1
            while True:
                url = f"https://api.github.com/user/repos?per_page=100&page={page}"
                req = Request(url)
                req.add_header("Authorization", f"token {token}")
                req.add_header("Accept", "application/vnd.github.v3+json")

                response = urlopen(req)
                data = json.loads(response.read().decode())

                if not data:
                    break

                all_repos.extend(data)
                page += 1

            loading_label.destroy()

            if not all_repos:
                no_repo_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text="📭 No repositories found",
                    font=ctk.CTkFont(size=14)
                )
                no_repo_label.grid(row=0, column=0, pady=20)
                return

            # Sort by name
            all_repos.sort(key=lambda x: x['name'].lower())
            self.all_repos = all_repos

            # Update title with count
            self.delete_title_label.configure(
                text=f"🗑 Delete GitHub Repositories ({len(all_repos)} repos)"
            )

            # Create checkboxes for each repo
            for idx, repo in enumerate(all_repos):
                repo_name = repo['name']
                repo_desc = repo.get('description', 'No description')
                if not repo_desc:
                    repo_desc = 'No description'

                # Create frame for each repo
                repo_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
                repo_frame.grid(row=idx, column=0, pady=5, padx=5, sticky="ew")
                repo_frame.grid_columnconfigure(1, weight=1)

                # Checkbox
                var = ctk.BooleanVar(value=False)
                checkbox = ctk.CTkCheckBox(
                    repo_frame,
                    text="",
                    variable=var,
                    width=30
                )
                checkbox.grid(row=0, column=0, padx=(5, 10))

                # Repo info
                info_frame = ctk.CTkFrame(repo_frame, fg_color="transparent")
                info_frame.grid(row=0, column=1, sticky="ew")

                name_label = ctk.CTkLabel(
                    info_frame,
                    text=f"📦 {repo_name}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w"
                )
                name_label.pack(anchor="w")

                desc_label = ctk.CTkLabel(
                    info_frame,
                    text=repo_desc[:100] + ('...' if len(repo_desc) > 100 else ''),
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                    anchor="w"
                )
                desc_label.pack(anchor="w")

                self.repo_checkboxes[repo_name] = {
                    'var': var,
                    'frame': repo_frame,
                    'repo_data': repo
                }

            self.log(f"✅ Loaded {len(all_repos)} repositories")

        except HTTPError as e:
            loading_label.destroy()
            if e.code == 401:
                error_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text="❌ Invalid credentials!",
                    font=ctk.CTkFont(size=14),
                    text_color="red"
                )
                error_label.grid(row=0, column=0, pady=20)
                self.log("❌ Invalid credentials")
            else:
                error_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=f"❌ Error loading repos: {e}",
                    font=ctk.CTkFont(size=14),
                    text_color="red"
                )
                error_label.grid(row=0, column=0, pady=20)
                self.log(f"❌ Error loading repos: {e}")
        except Exception as e:
            loading_label.destroy()
            error_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=f"❌ Unexpected error: {e}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.grid(row=0, column=0, pady=20)
            self.log(f"❌ Unexpected error: {e}")

    def filter_repos(self, event=None):
        """Filter repositories based on search text"""
        search_text = self.search_entry.get().lower()

        for repo_name, data in self.repo_checkboxes.items():
            if search_text in repo_name.lower():
                data['frame'].grid()
            else:
                data['frame'].grid_remove()

    def select_all(self):
        """Select all visible repositories"""
        for repo_name, data in self.repo_checkboxes.items():
            if data['frame'].winfo_manager():  # If visible
                data['var'].set(True)

    def deselect_all(self):
        """Deselect all repositories"""
        for data in self.repo_checkboxes.values():
            data['var'].set(False)

    def delete_selected(self):
        """Delete all selected repositories"""
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()

        selected_repos = [
            name for name, data in self.repo_checkboxes.items()
            if data['var'].get()
        ]

        if not selected_repos:
            messagebox.showwarning("Warning", "No repositories selected!")
            return

        # Confirmation
        count = len(selected_repos)
        repo_list = '\n'.join([f"  • {repo}" for repo in selected_repos[:10]])
        if count > 10:
            repo_list += f"\n  ... and {count - 10} more"

        confirm = messagebox.askyesno(
            "⚠️ Confirm Delete",
            f"Are you sure you want to delete {count} repository(ies)?\n\n{repo_list}\n\n⚠️ This action cannot be undone!"
        )

        if not confirm:
            return

        # Delete repositories
        success_count = 0
        failed_repos = []

        for repo_name in selected_repos:
            try:
                url = f"https://api.github.com/repos/{username}/{repo_name}"
                req = Request(url, method="DELETE")
                req.add_header("Authorization", f"token {token}")
                req.add_header("Accept", "application/vnd.github.v3+json")

                urlopen(req)
                self.log(f"✅ Deleted: {repo_name}")
                success_count += 1

                # Remove from history if exists
                if repo_name in self.history:
                    self.history.remove(repo_name)

            except HTTPError as e:
                self.log(f"❌ Failed to delete {repo_name}: {e}")
                failed_repos.append(repo_name)
            except Exception as e:
                self.log(f"❌ Error deleting {repo_name}: {e}")
                failed_repos.append(repo_name)

        # Save updated history
        self.save_history()

        # Show result
        result_msg = f"✅ Successfully deleted {success_count} repository(ies)"
        if failed_repos:
            result_msg += f"\n❌ Failed to delete {len(failed_repos)}:\n" + '\n'.join([f"  • {r}" for r in failed_repos[:5]])
            if len(failed_repos) > 5:
                result_msg += f"\n  ... and {len(failed_repos) - 5} more"

        messagebox.showinfo("Delete Complete", result_msg)

        # Reload repositories
        self.load_repos()

    # ================================
    # LOGS
    # ================================
    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def clear_logs(self):
        self.log_text.delete("1.0", "end")
        self.log("📜 Logs cleared.")

    # ================================
    # FOLDER HANDLING
    # ================================
    def load_saved_folders(self):
        """Load saved folders from local file"""
        if os.path.exists("saved_folders.txt"):
            with open("saved_folders.txt", "r", encoding="utf-8") as f:
                self.saved_folders = [line.strip() for line in f if line.strip()]

    def save_saved_folders(self):
        """Save folders to local file"""
        with open("saved_folders.txt", "w", encoding="utf-8") as f:
            for folder in self.saved_folders:
                f.write(folder + "\n")

    def save_current_folder(self):
        """Save current selected folder"""
        if not hasattr(self, 'selected_folder'):
            messagebox.showerror("Error", "Pilih folder terlebih dahulu!")
            return

        if self.selected_folder not in self.saved_folders:
            self.saved_folders.append(self.selected_folder)
            self.save_saved_folders()
            self.update_folder_dropdown()
            self.log(f"💾 Folder saved: {self.selected_folder}")
        else:
            self.log(f"⚠️ Folder already saved: {self.selected_folder}")

    def update_folder_dropdown(self):
        """Update folder dropdown menu"""
        if self.saved_folders:
            self.folder_optionmenu.configure(values=self.saved_folders)
        else:
            self.folder_optionmenu.configure(values=["No saved folders"])

    def select_saved_folder(self, selected):
        """Select folder from dropdown"""
        if selected and selected != "No saved folders":
            self.selected_folder = selected
            self.folder_label.configure(text=f"📂 Selected: {selected}")
            self.log(f"📂 Folder selected: {selected}")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_label.configure(text=f"📂 Selected: {folder}")

    def stop_push(self):
        self.stop_requested = True
        self.log("⏹ Push stopped by user.")

    def load_history(self):
        if os.path.exists("pushed_history.txt"):
            with open("pushed_history.txt", "r") as f:
                self.history = set(line.strip() for line in f)

    def save_history(self):
        with open("pushed_history.txt", "w") as f:
            for repo in self.history:
                f.write(repo + "\n")

    # ================================
    # GITHUB FUNCTIONS
    # ================================
    def get_owner_name(self, username):
        """Get owner name based on target type"""
        if self.target_type_var.get() == "Organization":
            org_name = self.org_entry.get().strip()
            if org_name:
                return org_name
            else:
                self.log("⚠️ Organization name is empty, using username")
                return username
        return username

    def get_existing_repos(self, username, token):
        try:
            owner = self.get_owner_name(username)
            
            # Check if it's an organization
            if self.target_type_var.get() == "Organization":
                url = f"https://api.github.com/orgs/{owner}/repos?per_page=100"
            else:
                url = f"https://api.github.com/users/{username}/repos?per_page=100"
            
            req = Request(url)
            req.add_header("Authorization", f"token {token}")
            req.add_header("Accept", "application/vnd.github.v3+json")
            response = urlopen(req)
            data = json.loads(response.read().decode())
            return {repo['name'] for repo in data}
        except HTTPError as e:
            if e.code == 401:
                self.log("❌ Username/Token salah! Push dihentikan.")
                self.invalid_credentials = True
            elif e.code == 404:
                self.log(f"❌ Organization '{owner}' tidak ditemukan!")
                self.invalid_credentials = True
            else:
                self.log(f"❌ Error fetching repos: {e}")
            return set()
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}")
            self.invalid_credentials = True
            return set()

    def create_github_repo(self, username, token, repo_name):
        base_name = repo_name
        counter = 1
        owner = self.get_owner_name(username)
        is_private = self.visibility_var.get() == "private"
        
        while True:
            try:
                # Different API endpoint for organizations
                if self.target_type_var.get() == "Organization":
                    url = f"https://api.github.com/orgs/{owner}/repos"
                    visibility_label = "🔒 Private" if is_private else "🌐 Public"
                    self.log(f"🏢 Creating {visibility_label} repo in organization: {owner}")
                else:
                    url = "https://api.github.com/user/repos"
                    visibility_label = "🔒 Private" if is_private else "🌐 Public"
                    self.log(f"👤 Creating {visibility_label} repo for user: {username}")
                
                req = Request(url, method="POST")
                req.add_header("Authorization", f"token {token}")
                req.add_header("Accept", "application/vnd.github.v3+json")
                req.add_header("Content-Type", "application/json")
                
                # Add private parameter to the payload
                post_data = json.dumps({
                    "name": repo_name, 
                    "auto_init": False,
                    "private": is_private
                }).encode()
                
                urlopen(req, post_data)
                visibility_emoji = "🔒" if is_private else "🌐"
                self.log(f"✅ Created {visibility_emoji} repo: {repo_name}")
                return repo_name
            except HTTPError as e:
                if e.code == 422:
                    repo_name = f"{base_name}-{counter}"
                    counter += 1
                    self.log(
                        f"⚠️ Repo {base_name} sudah ada, mencoba {repo_name}...")
                elif e.code == 401:
                    self.log(
                        "❌ Username/Token salah saat create repo! Push dihentikan.")
                    self.invalid_credentials = True
                    return None
                elif e.code == 404:
                    self.log(
                        f"❌ Organization '{owner}' tidak ditemukan atau tidak punya akses!")
                    self.invalid_credentials = True
                    return None
                else:
                    self.log(f"❌ Error creating repo {repo_name}: {e}")
                    return None
            except Exception as e:
                self.log(f"❌ Unexpected error creating repo {repo_name}: {e}")
                self.invalid_credentials = True
                return None

    def sanitize_repo_name(self, name):
        """Sanitize repository name"""
        if self.replace_space_var.get():
            name = name.replace(" ", "-")
        return name

    def init_and_push(self, folder_path, repo_name, username, token, existing_repos):
        if self.invalid_credentials:
            return

        # Sanitize repo name
        repo_name = self.sanitize_repo_name(repo_name)
        owner = self.get_owner_name(username)

        if repo_name in existing_repos or repo_name in self.history:
            self.log(f"⚠️ Skipping {repo_name}: Already exists or pushed.")
            return
        os.chdir(folder_path)
        try:
            if not os.path.exists(".git"):
                subprocess.check_call(["git", "init"])
                subprocess.check_call(["git", "branch", "-M", "main"])
                self.log(f"Initialized git in {folder_path}")
            subprocess.check_call(["git", "add", "."])
            try:
                subprocess.check_call(
                    ["git", "commit", "-m", "Initial commit"])
            except subprocess.CalledProcessError:
                self.log("No changes to commit, proceeding.")
            if repo_name not in existing_repos:
                created_repo = self.create_github_repo(
                    username, token, repo_name)
                if not created_repo:
                    return
                repo_name = created_repo
            
            # Use owner (username or org name) for remote URL
            remote_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
            try:
                subprocess.check_call(
                    ["git", "remote", "add", "origin", remote_url])
            except subprocess.CalledProcessError:
                subprocess.check_call(
                    ["git", "remote", "set-url", "origin", remote_url])
            try:
                subprocess.check_call(["git", "push", "-u", "origin", "main"])
                self.log(f"✅ Pushed {repo_name} successfully to {owner}.")
            except subprocess.CalledProcessError:
                self.log("❌ Push gagal. Push dihentikan.")
                self.invalid_credentials = True
            self.history.add(repo_name)
            self.save_history()
        finally:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

    def process_projects(self, projects, index, username, token, existing_repos):
        if self.stop_requested or self.invalid_credentials:
            self.log("⏹ Push dihentikan.")
            self.progress.set(0)
            return
        if index >= len(projects):
            self.log("🎉 Process completed.")
            self.progress.set(1)
            return
        folder_path, repo_name = projects[index]
        self.log(f"🔄 Processing {repo_name}...")
        self.init_and_push(folder_path, repo_name,
                           username, token, existing_repos)
        self.progress.set((index + 1) / len(projects))
        self.after(1500, lambda: self.process_projects(
            projects, index + 1, username, token, existing_repos))

    def scan_and_push(self):
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()
        
        if not username or not token or not hasattr(self, 'selected_folder'):
            messagebox.showerror(
                "Error", "Please fill all fields and select folder.")
            return
        
        # Validate organization if selected
        if self.target_type_var.get() == "Organization":
            org_name = self.org_entry.get().strip()
            if not org_name:
                messagebox.showerror(
                    "Error", "Please enter organization name or select from dropdown!")
                return
            self.log(f"🏢 Target: Organization '{org_name}'")
        else:
            self.log(f"👤 Target: User account '{username}'")
        
        # Log visibility setting
        visibility = self.visibility_var.get()
        visibility_emoji = "🔒 Private" if visibility == "private" else "🌐 Public"
        self.log(f"🔧 Repository Visibility: {visibility_emoji}")
        
        self.invalid_credentials = False
        self.log("🚀 Starting scan and push...")
        self.stop_requested = False
        existing_repos = self.get_existing_repos(username, token)
        if self.invalid_credentials:
            self.username_entry.focus()
            return
        if not existing_repos:
            self.log("⚠️ Failed to fetch existing repos, proceeding anyway.")

        projects = []
        if self.sort_by_year_var.get():
            # Folder berdasarkan tahun
            year_folders = [f for f in os.listdir(self.selected_folder)
                            if os.path.isdir(os.path.join(self.selected_folder, f)) and re.match(r"^\d{4}$", f)]
            if not year_folders:
                self.log("⚠️ No year-based subfolders found.")
                return
            year_folders.sort(key=lambda x: int(x))
            for year in year_folders:
                year_path = os.path.join(self.selected_folder, year)
                for project in os.listdir(year_path):
                    if project.startswith('.'):
                        continue  # Skip hidden folders like .git
                    project_path = os.path.join(year_path, project)
                    if os.path.isdir(project_path):
                        repo_name = f"{year}-{project}"
                        projects.append((project_path, repo_name))
        else:
            # Semua folder di level ini
            for project in os.listdir(self.selected_folder):
                if project.startswith('.'):
                    continue  # Skip hidden folders like .git
                project_path = os.path.join(self.selected_folder, project)
                if os.path.isdir(project_path):
                    repo_name = project
                    projects.append((project_path, repo_name))

        if not projects:
            self.log("⚠️ No projects found to push.")
            return

        self.progress.set(0)
        self.process_projects(projects, 0, username, token, existing_repos)


if __name__ == "__main__":
    app = GitHubPusherApp()
    app.mainloop()