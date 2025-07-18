import requests
import json
import os
import math

# List of repository URLs to fetch
repo_urls = [
    "https://quarksources.github.io/dist/altstore-complete.min.json",
    "https://repository.apptesters.org",
    "https://raw.githubusercontent.com/usearcticsigner/Arctic-Repo/refs/heads/main/repo.json",
    "https://ipa.cypwn.xyz/cypwn.json",
    "https://github.com/khcrysalis/Feather/raw/main/app-repo.json",
    "https://flyinghead.github.io/flycast-builds/altstore.json",
    "https://cdn.dbservices.to/repo-jsons/c57a4ad1304d231dbbd7a77d21448bdeab1bbaf2.json",
    "https://raw.githubusercontent.com/Neoncat-OG/TrollStore-IPAs/refs/heads/main/apps_esign.json?v=1",
    "https://altstore.oatmealdome.me",
    "https://alt.crystall1ne.dev",
    "https://provenance-emu.com/apps.json",
    "https://quarksources.github.io/dist/quantumsource.min.json",
    "https://quarksources.github.io/dist/quantumsource%2B%2B.min.json",
    "https://cdn.dbservices.to/repo-jsons/9a470cb1c1dd49f9ec157d29ee36626e011b4436.json",
    "https://cdn.dbservices.to/repo-jsons/aa04d8c31a56e63c1a047534e86798546a8f1e08.json",
    "https://alt.getutm.app",
    "https://wuxu1.github.io/wuxu-complete-plus.json",
    "https://raw.githubusercontent.com/driftywinds/driftywinds.github.io/master/AltStore/apps.json",
    "https://esign.yyyue.xyz/app.json"
]

# Get the repository owner and name from environment variables
repo_owner = os.environ.get('GITHUB_REPOSITORY_OWNER')
repo_name = os.environ.get('GITHUB_REPOSITORY_NAME')

# Ensure the environment variables are set before constructing the sourceURL
if not repo_owner or not repo_name:
    print("Error: GITHUB_REPOSITORY_OWNER and GITHUB_REPOSITORY_NAME environment variables are not set.")
    # Fallback for local testing
    source_url = "https://raw.githubusercontent.com/kbdevs/repo-aggregator/main/combined.json"
else:
    source_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/combined.json"


def aggregate_sources():
    """Fetches all apps from the source list and combines them, removing duplicates."""
    all_apps = []
    processed_bundle_ids = set()
    
    print("Starting repo aggregation...")

    for url in repo_urls:
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            repo_data = response.json()
            
            if "apps" in repo_data and isinstance(repo_data["apps"], list):
                apps_count = 0
                for app in repo_data["apps"]:
                    if "bundleIdentifier" in app and app["bundleIdentifier"] not in processed_bundle_ids:
                        all_apps.append(app)
                        processed_bundle_ids.add(app["bundleIdentifier"])
                        apps_count += 1
                print(f"-> Found and added {apps_count} new app(s).")
            else:
                print(f"-> Warning: 'apps' key not found or not a list in {url}")

        except requests.exceptions.RequestException as e:
            print(f"-> Error fetching {url}: {e}")
        except json.JSONDecodeError:
            print(f"-> Error: Could not decode JSON from {url}.")
        except Exception as e:
            print(f"-> An unexpected error occurred for {url}: {e}")

    combined_repo = {
        "name": "Combined AltStore Repo",
        "identifier": "kbdevs.altstore",
        "sourceURL": source_url,
        "apps": all_apps,
        "userInfo": {}
    }

    with open("combined.json", "w") as outfile:
        json.dump(combined_repo, outfile, indent=2)
        
    print(f"\nAggregation complete. Total unique apps: {len(all_apps)}.")
    print("The combined file 'combined.json' has been created.")
    
    return combined_repo

def split_repo(combined_data, num_chunks=12):
    """Splits the combined repo data into a specified number of chunks."""
    apps = combined_data.get("apps", [])
    if not apps:
        print("No apps to split.")
        return

    total_apps = len(apps)
    chunk_size = math.ceil(total_apps / num_chunks)
    
    print(f"\nSplitting {total_apps} apps into {num_chunks} files...")

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = start_index + chunk_size
        app_chunk = apps[start_index:end_index]

        if not app_chunk:
            continue

        chunk_repo = {
            "name": f"Combined AltStore Repo - Part {i + 1}",
            "identifier": f"kbdevs.altstore.chunk{i + 1}",
            "sourceURL": source_url.replace("combined.json", f"chunk_{i + 1}.json"),
            "apps": app_chunk,
            "userInfo": {}
        }
        
        file_name = f"chunk_{i + 1}.json"
        with open(file_name, "w") as chunk_file:
            json.dump(chunk_repo, chunk_file, indent=2)
        
        print(f"-> Created {file_name} with {len(app_chunk)} apps.")

if __name__ == "__main__":
    combined_repository_data = aggregate_sources()
    if combined_repository_data:
        split_repo(combined_repository_data)
