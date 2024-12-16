import sass
import os

def compile_scss():
    # Get the absolute path to the static directory
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static')
    scss_path = os.path.join(static_dir, 'scss', 'main.scss')
    css_path = os.path.join(static_dir, 'css', 'main.css')

    # Create css directory if it doesn't exist
    os.makedirs(os.path.dirname(css_path), exist_ok=True)

    # Compile SCSS to CSS
    css = sass.compile(filename=scss_path, output_style='compressed')
    
    # Write the compiled CSS to file with UTF-8 encoding
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)

    print(f"SCSS compiled successfully to {css_path}")

if __name__ == '__main__':
    compile_scss()
