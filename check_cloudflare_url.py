from upgrad_url import upgrad_prod_url
import subprocess

def is_cloudflare(url):
    try:
        # Run host command
        result = subprocess.check_output(["host", url], stderr=subprocess.STDOUT)
        output = result.decode().lower()

        #Cloudflare indicators
        cloudflare_keywords = [
            "cloudflare", 
            "cf", 
            "cdn.cloudflare.net"
        ]

        return any(keyword in output for keyword in cloudflare_keywords)

    except subprocess.CalledProcessError:
        return False


for url in upgrad_prod_url:
    if is_cloudflare(url):
        print(f"{url} --> YES (behind Cloudflare)")
    else:
        print(f"{url} --> NO (not Cloudflare)")