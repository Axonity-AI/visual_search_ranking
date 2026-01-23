import os
import random
import shutil

def create_shorter_dataset(source_folder, destination_folder, min_images=3, max_images=5):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for subfolder_name in os.listdir(source_folder):
        subfolder_path = os.path.join(source_folder, subfolder_name)
        if os.path.isdir(subfolder_path):
            destination_subfolder_path = os.path.join(destination_folder, subfolder_name)
            if not os.path.exists(destination_subfolder_path):
                os.makedirs(destination_subfolder_path)

            images = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
            selected_images = random.sample(images, min(len(images), random.randint(min_images, max_images)))

            for image in selected_images:
                source_image_path = os.path.join(subfolder_path, image)
                destination_image_path = os.path.join(destination_subfolder_path, image)
                shutil.copy2(source_image_path, destination_image_path)

source_folder = r"C:\Users\Anurag\Desktop\Axonity\client_projects\memeraki\demo_project\archive\images"
destination_folder = r"C:\Users\Anurag\Desktop\Axonity\client_projects\memeraki\demo_project\archive\images_shorter"
create_shorter_dataset(source_folder, destination_folder)
