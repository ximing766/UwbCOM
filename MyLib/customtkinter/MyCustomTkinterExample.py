import customtkinter as ctk
import customtkinter
import os
from PIL import Image


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.width = 700
        self.height = 450
        self.version = "_v1.0"
        self.title("example" + self.version)
        self.geometry("{}x{}".format(self.width, self.height))


        self.RootFrame = customtkinter.CTkFrame(self, corner_radius=0)
        self.RootFrame.pack(fill="both", expand=True)
        self.attributes("-transparentcolor", "white")
        # set grid layout 1x2
        self.RootFrame.grid_rowconfigure(0, weight=1)
        self.RootFrame.grid_columnconfigure(1, weight=1)   #界面变化时导航列0不会变宽
        self.Init_image()
        
        self.create_navigation_page()
        self.create_home_page()
        self.create_second_page()
        self.create_third_page()
        
        self.select_page_by_name("home")
    
    def create_navigation_page(self):
        self.navigation_frame = customtkinter.CTkFrame(self.RootFrame, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="Example", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.page_home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",fg_color="transparent", 
                                                   anchor="w", command=self.page_home_button_event, font=customtkinter.CTkFont(size=12, weight="bold"), image=self.my_ico)
        self.page_home_button.grid(row=1, column=0, sticky="ew")

        self.page_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 2",fg_color="transparent", 
                                                    anchor="w", command=self.page_2_button_event, font=customtkinter.CTkFont(size=12, weight="bold"))
        self.page_2_button.grid(row=2, column=0, sticky="ew")

        self.page_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3",fg_color="transparent", 
                                                    anchor="w", command=self.page_3_button_event, font=customtkinter.CTkFont(size=12, weight="bold"))
        self.page_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
    
    def create_home_page(self):
        self.home_frame = ctk.CTkFrame(self.RootFrame, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame_large_image_label = ctk.CTkLabel(self.home_frame, text="Home page", font=ctk.CTkFont(size=20, weight="bold"))
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

        # 添加 CTkScrollableFrame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.home_frame)
        self.scrollable_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        # 添加 2 个按钮
        self.button_1 = ctk.CTkButton(self.scrollable_frame, text="Button 1")
        self.button_1.grid(row=0, column=0, padx=10, pady=5)
        self.button_2 = ctk.CTkButton(self.scrollable_frame, text="Button 2")
        self.button_2.grid(row=1, column=0, padx=10, pady=5)
        # 添加 2 个输入框
        self.entry_1 = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Entry 1")
        self.entry_1.grid(row=2, column=0, padx=10, pady=5)
        self.entry_2 = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Entry 2")
        self.entry_2.grid(row=3, column=0, padx=10, pady=5)
        # 添加 2 个复选框
        self.checkbox_1 = ctk.CTkCheckBox(self.scrollable_frame, text="Checkbox 1")
        self.checkbox_1.grid(row=4, column=0, padx=10, pady=5)
        self.checkbox_2 = ctk.CTkCheckBox(self.scrollable_frame, text="Checkbox 2")
        self.checkbox_2.grid(row=5, column=0, padx=10, pady=5)
        # 添加 2 个标签
        self.label_1 = ctk.CTkLabel(self.scrollable_frame, text="Label 1")
        self.label_1.grid(row=6, column=0, padx=10, pady=5)
        self.label_2 = ctk.CTkLabel(self.scrollable_frame, text="Label 2")
        self.label_2.grid(row=7, column=0, padx=10, pady=5)

    
    def create_second_page(self):
        self.second_frame = customtkinter.CTkFrame(self.RootFrame, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_columnconfigure(0, weight=1)
        self.second_frame_large_image_label = customtkinter.CTkLabel(self.second_frame, text="Second page", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.second_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

    def create_third_page(self):
        self.third_frame = customtkinter.CTkFrame(self.RootFrame, corner_radius=0, fg_color="transparent")
        self.third_frame.grid_columnconfigure(0, weight=1)
        self.third_frame_large_image_label = customtkinter.CTkLabel(self.third_frame, text="Thrid page", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.third_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

    def select_page_by_name(self, name):
        self.pages = {
            "home": self.home_frame,
            "page_2": self.second_frame,
            "page_3": self.third_frame
        }
        # set button color for selected button
        self.page_home_button.configure(fg_color=("#17A2B8", "#0c5460") if name == "home" else "transparent")
        self.page_2_button.configure(fg_color=("#17A2B8", "#0c5460") if name == "page_2" else "transparent")
        self.page_3_button.configure(fg_color=("#17A2B8", "#0c5460") if name == "page_3" else "transparent")

        for page_name,frame in self.pages.items():
            if name == page_name:
                frame.grid(row=0, column=1, sticky="nsew")
            else:
                frame.grid_forget()

    def page_home_button_event(self):
        self.select_page_by_name("home")

    def page_2_button_event(self):
        self.select_page_by_name("page_2")

    def page_3_button_event(self):
        self.select_page_by_name("page_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def Init_image(self):
        image_path = os.path.dirname(__file__) + "\\test_images"
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "HomePage.png")), size=(500, 150))
        self.my_ico = customtkinter.CTkImage(Image.open("E:\\Work\\UWB\\Code\\UwbCOMCode\\PIC\\my.png"), size=(32, 32))


if __name__ == "__main__":
    customtkinter.set_appearance_mode("light")                            # Modes: System (default), light, dark
    file = os.path.join(os.path.dirname(__file__), "MyMoo" + ".json")     # MyMoo  TestCardNew
    customtkinter.set_default_color_theme(file)
    app = App()

    app.mainloop()
