Let's going to create a database where we are going to store the survey data and the analysis results.

### Tech Stack
- SQL
- Supabase

### Survey Data
- Each time we run the code, we are going to save the survey data in a csv file.
- We are going to store the csv file in the `data` folder.
- The name of the file should be the date and time when the survey was taken.
- After the execution of the code, we are going to delete the csv file.

- Here we need a table with the following columns:
    - id: uuid
    - survey_data: .csv
    - company_name: string
    - company_description: string
    - company_size: string
    - company_industry: string
    - company_location: string
    - company_website: string
    - company_email: string
    - company_phone: string


### Analysis Results - DONE
- We are going to store the analysis results in an md file.
- The results are going to be stored in the 'Desktop' folder of the user.
- A nice idea would be to pass the md file for a latex compiler to generate a pdf. And directly save the pdf in the 'Desktop' folder of the user.
    - we have to send it to a LLM to generate the latex code from the md file.

### RAG
- We are going to use a RAG to access information about the company just in case it's local calculus
- We are going to store the RAG in a vector database.


