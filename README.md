# Verse-Jan25-Prj

## Spotify Rate Limited Ingestion

A Python project designed to ingest (theoretically) all artists from the Spotify API as quickly as possible while respecting rate limits and ensuring resilience.

---

### Overview

This project showcases a **best-effort** approach to discover as many Spotify artists as possible by leveraging multiple ingestion strategies. It is built with robustness and long-running capabilities in mind, making it suitable for large-scale data collection scenarios.

---

### Key Features

- **Two Ingestion Strategies**
  1. **Search Strategy**: Uses Spotify’s `/search` endpoint. Generates a wide range of queries (letters, digits, and special characters) to systematically discover new artists.
  2. **Related Strategy**: Starts from a seed list (e.g., trending artists) and iteratively explores each artist’s related artists to uncover new IDs.

- **Rate Limiting**
  - A token bucket rate limiter that adapts to Spotify’s constraints and automatically retries on `429 (Too Many Requests)` responses.

- **Resilient & Long-Running**
  - **Checkpointing**: The script persistently saves progress (`visited_ids` and `to_process`) so that it can resume after failure or interruption (e.g., keyboard interrupt).
  - **Token Refresh**: Automatically fetches and refreshes Spotify tokens when they expire or are invalid.

- **Configurable**
  - Command-line arguments allow you to:
    - Provide Spotify credentials via CLI or environment variables.
    - Choose between **search** or **related** ingestion strategies.
    - Configure rate limit (`--max-calls`, `--period`).
    - Specify output CSV file and checkpoint file paths.

- **Unit Tested**
  - Comprehensive tests for:
    - Rate Limiter (token bucket logic, blocking under load).
    - Spotify Client (auth flow, search, error handling).
    - Storage (saving artist data to CSV).
    - Auth Manager (fetches and refreshes tokens).
    - Strategies (both Search and Related).

---

### Project Structure

```
verse/
├── main.py                  # Entry point script
├── auth_manager.py          # Handles Spotify OAuth client credentials
├── rate_limiter.py          # Token-bucket rate limiting implementation
├── spotify.py               # Spotify client wrapper
├── storage.py               # CSV-based storage + checkpoint logic
├── models.py                # Pydantic models for validation
├── strategies
│   ├── base_strategy.py     # Abstract base strategy
│   ├── search_strategy.py   # "Search" ingestion strategy
│   └── related_strategy.py  # "Related artists" ingestion strategy
├── tests                    # Unit tests
│   ├── test_*.py
│   └── ...
├── requirements.txt
└── README.md                # This file
```

---

### Installation & Setup

#### 1. Installing from PyPI (Recommended)

If you’ve published this package to PyPI under the name `verse-jan25-prj`, you (or anyone else) can install it directly:

```bash
pip install verse-jan25-prj
```

Then you can run the command-line entry point:

```bash
verse-jan25-prj --help
```

This will display all the available command-line options (similar to those in the [Usage](#usage) section below).

---

#### 2. Cloning the Repository (Local Install)

Alternatively, if you’re working directly from this GitHub repo:

1. **Clone or download this repository**

    ```bash
    git clone https://github.com/YOUR_USERNAME/Verse-Jan25-Prj.git
    cd Verse-Jan25-Prj
    ```

2. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Obtain Spotify API credentials**
    - Register or log in at [Spotify Developer](https://developer.spotify.com/dashboard/) to create a new app.
    - Copy your Client ID and Client Secret.

4. **Set credentials (choose one)**:
    - **Option A: Environment Variables**

        ```bash
        export SPOTIFY_CLIENT_ID="YOUR_CLIENT_ID"
        export SPOTIFY_CLIENT_SECRET="YOUR_CLIENT_SECRET"
        ```

    - **Option B: Pass via CLI arguments**

        ```bash
        --client-id YOUR_CLIENT_ID
        --client-secret YOUR_CLIENT_SECRET
        ```

---

### Usage

#### Running the CLI

- **If installed via PyPI**:

    ```bash
    verse-jan25-prj [OPTIONS]
    ```

- **If running from source (the local cloned repo)**:

    ```bash
    python main.py [OPTIONS]
    ```

#### Common Arguments

- **`--client-id`**  
  Your Spotify Client ID (if not set in environment variable).

- **`--client-secret`**  
  Your Spotify Client Secret (if not set in environment variable).

- **`--strategy`**  
  - `search` (default) – uses the search queries approach.
  - `related` – explores related artists from seeds.

- **`--output`**  
  Output CSV file for storing results. (Default: `artists.csv`)

- **`--checkpoint`**  
  JSON file for storing progress. (Default: `.cache/spotify_ingest_checkpoint.json`)

- **`--max-calls`**  
  Max requests per second. (Default: `1`)

- **`--period`**  
  Rolling window (in seconds) for the token bucket. (Default: `1.0`)

---

#### Example Commands

1. **Search Strategy (using environment variables)**:

    ```bash
    verse-jan25-prj --strategy search --max-calls 5 --period 1.0
    ```

    This will:
    - Use your environment variables for Spotify credentials.
    - Attempt up to 5 requests per second.
    - Search by systematically generating queries (letters, digits, `_`, `-`, `&`, space, etc.).

2. **Related Strategy (passing credentials via CLI)**:

    ```bash
    verse-jan25-prj \
        --client-id 123abc \
        --client-secret 456xyz \
        --strategy related \
        --max-calls 10 \
        --period 0.5
    ```

    This will:
    - Start from a seed of _trending artists_ (in this example, a placeholder method is used).
    - Expand outward by repeatedly fetching each artist’s related artists.
    - Use a higher rate limit (up to 10 calls every 0.5 seconds).

If the script is interrupted, re-running the same command will resume from the checkpoint (unless you delete that file).

---

### Design & Approach

1. **Ingestion Strategies**
    - **SearchIngestionStrategy**:  
      Enumerates multiple queries (a-z, 0-9, special chars) to find new artists from Spotify’s `/search` endpoint. This helps "coax" the data from the API since Spotify does not provide a single "all artists" endpoint.
    - **RelatedArtistsIngestionStrategy**:  
      Begins with a user-defined (or "trending") set of artists, then crawls each artist’s "related artists" to discover new IDs.

2. **Rate Limiting & Resilience**
    - **Token Bucket**:  
      Our `RateLimiter` class ensures we don’t exceed the allowed number of requests. When tokens run out, the script blocks briefly to avoid hitting the rate limit.
    - **Auto-Retry**:  
      Handles `429` responses by respecting `Retry-After` headers.
    - **Auth Refresh**:  
      If a request is `401 (Unauthorized)`, we automatically fetch a new token and retry.

3. **Checkpointing**
    - Each run saves the sets of **visited_ids** and **to_process** to a JSON file.
    - On startup, the script resumes from the last checkpoint, making it resilient against crashes, timeouts, or manual interruptions.

4. **Data Storage**
    - Default is CSV via `CSVStorage`, but you can easily replace or extend storage (e.g., database) by implementing a custom `.save_artist()` method.

5. **Testing**
    - The `tests/` folder contains unit tests for major modules (strategies, rate limiter, auth manager, storage, etc.).
    - Mocking is used extensively to avoid hitting Spotify’s real API or requiring network access during tests.

---

### Running Tests

From the project root, you can run:

```bash
pytest
```

It will discover and run all test files in the `tests/` directory.

---

### Notes

- This code is provided as a demonstration of architecture, rate-limiting logic, and robust data ingestion strategies.
- Real usage may require further refinements (e.g., handling additional edge cases, deeper logging, or storing more complex data).

---

### Conclusion

**Verse-Jan25-Prj** exemplifies a robust backend engineering solution for large-scale artist ingestion from Spotify. By combining:

- Token-based rate limiting,
- Multiple ingestion strategies,
- Checkpoint-based resilience,
- And thorough testing,

…it stands ready to theoretically ingest millions of artists while adhering to Spotify’s constraints.

I know I went a little overboard, but I honestly hate the interviewing process and wanted to make a good impression.

**Thank you for checking it out!**