# Lab2 Write-up

## 1. What the lab was about

The main goals for this lab were:
1.  **Practice and understand better:** To get better at the ideas learned in Lab1 by using them in a more real-world situation.
2.  **Use new tools:** To change the app from using a simple local database (SQLite) to a cloud database (Supabase) and put it online using Vercel.
3.  **Learn the process:** To practice the whole modern deployment process, from local development to putting the app on the internet.
4.  **Think about using AI helpers:** To try using AI tools (like Copilot) for coding and see what is good and what is difficult.

## 2. What I did (Main Steps)

### 2.1 Starting Point: Finishing Lab1's work

I did not finish Lab1 on time, so I started by doing that work first.
-   **Using the AI tool:** I used the `manus` AI tool to create the starting code for the app, as the guide said.
-   **Problem with technology choice:** My first tries asked the AI to use Node.js for the backend, but it failed twice (taking about 30 minutes). It only worked when I switched to using Python for the backend.
-   **Result:** I got a basic app that could run on my computer.

### 2.2 Changing the Database: From SQLite to Supabase

This was the main task for Lab2.

1.  **Making a Supabase project:** I went to the Supabase website and created a new project. I saved the connection details (URL and secret Key).
2.  **Using AI to change the code:** I asked the AI to change the app's code. The goal was to make the app talk to the new Supabase database online instead of the local SQLite one.
    -   The AI changed the code in the frontend (React) to send requests to Supabase's API.
3.  **Setting up environment variables:** To keep the secret Key safe, I used environment variables.
    -   **On my computer:** I made a `.env.local` file to hold the secret Key.
    -   **On Vercel:** I added the same secret keys to the Vercel website for my project.

### 2.3 Putting the App Online: Using Vercel

1.  **Connecting the code:** I logged into Vercel and connected it to my project's code on GitHub.
2.  **Configuring the project:** Vercel automatically understood it was a React app.
3.  **Adding the secret keys:** I added the Supabase URL and Key to Vercel's settings so the online app could find the database.
4.  **Deploying:** Vercel built the app and gave me a public website address.

### 2.4 Fixing Problems

After deploying, the app did not work correctly. I found two big problems.

-   **Problem 1: How to connect to Supabase**
    -   **What happened:** The online app could not get any data.
    -   **The fix:** The AI's code tried to connect the wrong way. **By reading the Supabase official docs myself**, I learned that for free plans on Vercel, you must use a special "connection pool" URL. I changed the website address in my code to fix this. The AI did not know about this rule.

-   **Problem 2: A library didn't work online**
    -   **What happened:** Some parts of the app looked broken online, even though they worked on my computer.
    -   **The fix:** I think a UI component library I used was not fully compatible with Vercel. It was hard to find the error from the logs. I finally fixed it by replacing that library with a more common and stable one.

## 3. What I learned and the challenges

### 3.1 Using AI helpers

1.  **The good parts:**
    -   **Very fast for common tasks:** It is great for writing simple, repetitive code that many people use (like basic database operations).
    -   **Understands the project:** The AI in the IDE can see all my code and give relevant suggestions.

2.  **The big problems:**
    -   **It can be confidently wrong:** The AI sometimes gives answers that look right but are actually wrong ("AI hallucinations"). The Supabase connection problem is a good example. It doesn't know specific rules for different services.
    -   **Not good with less popular tools:** It works best with very common technology choices.
    -   **Hard to fix errors:** When the AI changes a lot of code and makes a mistake, it is very difficult to find and fix the problem.
    -   **Can get slow:** When the conversation with the AI gets long, it takes more time to think of an answer.

### 3.2 Main lessons for me

-   **The AI is a helper, not the boss.** I should use it for small, clear tasks. I must still make the big decisions and understand what the code is doing.
-   **Always check the official website.** The official documentation (like Supabase's docs) is the most reliable source of information. I cannot trust the AI for important details.
-   **Test changes in small steps.** I should not let the AI change too much code at once. It is better to make small changes and check that they work.
-   **Things can be different online.** An app that works on my computer might not work on a service like Vercel. I need to think about the online environment.

## 4. Time spent

-   **Total time for Lab2:** About 4 hours.
-   **Catching up on Lab1:** About 2 hours of that was finishing the Lab1 work.
-   **For the Lab2 tasks:** I spent about 2 hours.
    -   The first hour was letting the AI try to do most of the work, which caused problems.
    -   The second hour was me fixing the problems that the AI could not solve.
