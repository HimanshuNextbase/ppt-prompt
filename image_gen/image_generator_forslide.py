import os
import requests
import fal_client
import argparse
def ensure_fal_key():
    """
    Ensures FAL_KEY is present in the environment.

    Security note:
    - Do NOT hardcode API keys in source control.
    - Set FAL_KEY in your shell before running this script.
    """
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        # Fallback to a locally-defined key if present (NOT recommended to commit).
        fal_key = globals().get("FAL_KEY")

    if not fal_key:
        raise RuntimeError(
            "Missing FAL_KEY. Set it first (PowerShell):\n"
            '  $env:FAL_KEY=\"YOUR_KEY_HERE\"'
        )

    os.environ["FAL_KEY"] = fal_key

def generate_image_from_text(prompt, aspect_ratio="16:9", output_file="generated_image.png"):
    """
    Generates an image from a text prompt using fal-ai/nano-banana model.
    
    Args:
        prompt (str): The description of the image to generate.
        aspect_ratio (str): The aspect ratio (e.g., "16:9", "1:1", "4:3"). Default is "16:9".
        output_file (str): The local filename to save the image to. Default is "generated_image.png".
        
    Returns:
        str: The path to the saved image file, or None if failed.
    """
    print(f"Generating image for prompt: '{prompt}'")
    print(f"Aspect Ratio: {aspect_ratio}")
    
    try:
        # Subscribe to the generation process
        handler = fal_client.submit(
            "fal-ai/nano-banana",
            arguments={
                "prompt": prompt,
                "aspect_ratio": aspect_ratio
            },
        )
        print("Request submitted... waiting for result.")
        
        # Get the result
        result = fal_client.result("fal-ai/nano-banana", handler.request_id)
        
        if result and "images" in result and len(result["images"]) > 0:
            image_info = result["images"][0]
            image_url = image_info["url"]
            print(f"Image generated successfully! URL: {image_url}")
            
            # Download the image
            print("Downloading image...")
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"Image saved locally to: {os.path.abspath(output_file)}")
                return output_file
            else:
                print(f"Failed to download image. Status code: {response.status_code}")
                return None
        else:
            print("No images returned in the result.")
            return None
            
    except Exception as e:
        print(f"An error occurred during image generation: {e}")
        return None

if __name__ == "__main__":
    print("--- Text to Image Generator (fal-ai/nano-banana) ---")

    parser = argparse.ArgumentParser(description="Generate an image from a text prompt using fal-ai/nano-banana.")
    parser.add_argument("--prompt", type=str, help="Text prompt for image generation.")
    parser.add_argument("--ar", type=str, default="16:9", help="Aspect ratio (default: 16:9).")
    parser.add_argument("--out", type=str, default="generated_image.png", help="Output filename (default: generated_image.png).")
    args = parser.parse_args()

    try:
        ensure_fal_key()
    except Exception as e:
        print(str(e))
        raise SystemExit(1)

    user_prompt = args.prompt or input("Enter your image prompt: ").strip()
    if not user_prompt:
        print("Prompt cannot be empty.")
        raise SystemExit(2)

    user_ar = args.ar
    if not args.prompt:
        ar_in = input("Enter aspect ratio (default 16:9, options: 16:9, 1:1, 4:3, etc.): ").strip()
        if ar_in:
            user_ar = ar_in

    generate_image_from_text(user_prompt, user_ar, output_file=args.out)
