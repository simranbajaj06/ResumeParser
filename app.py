import streamlit as st
import os
import shutil
import zipfile
from io import BytesIO
from resumeParser import parser
# from test import filter_resumes

st.title("Resume Semantic Search")

job_description = st.text_area("Enter Job Description")
folder_path=st.text_area("Enter Resume Folder path")
if st.button("Process Resumes"):
    if  job_description:
        
        matching_candidates = parser(folder_path, job_description)

        if matching_candidates:
            st.success("Matching candidates found!")
            
            # Display matching candidates and create a zip file for download
            with zipfile.ZipFile("matching_resumes.zip", "w") as zipf:
                files = matching_candidates.split(',')

                # Strip any leading/trailing whitespace from each file path
                files = [file.strip() for file in files]

                # Extract filenames from the file paths
                filenames = [os.path.basename(file) for file in files]

                for pdf_filename in filenames:
                    st.write(f"Candidate: {pdf_filename}")
                    zipf.write(os.path.join(folder_path, pdf_filename), arcname=pdf_filename)

            # Provide a download button for the zip file
            with open("matching_resumes.zip", "rb") as f:
                st.download_button(
                    label="Download All Matching Resumes",
                    data=f,
                    file_name="matching_resumes.zip",
                    mime="application/zip"
                )
        else:
            st.warning("No matching candidates found.")
        
        # Clean up the temporary folder
     
        os.remove("matching_resumes.zip")
    else:
        st.error("Please upload resumes and enter a job description.")
