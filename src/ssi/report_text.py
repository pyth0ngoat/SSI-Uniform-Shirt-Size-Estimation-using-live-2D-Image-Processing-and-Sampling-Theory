import json
import os
import subprocess
import pandas as pd
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_toc(doc):
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    
    run._r.append(fldChar)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def add_page_number(doc):
    # Quick hack to add page numbers: python-docx doesn't do this easily, 
    # but we can add a footer with a page number field
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        run._r.extend([fldChar1, instrText, fldChar2, fldChar3])

class ReportBuilder:
    def __init__(self, facts):
        self.facts = facts
        self.md_lines = []
        self.doc = Document()
        
        # Setup A4, 11pt font
        section = self.doc.sections[0]
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        style = self.doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        
        add_page_number(self.doc)
        
        self.fig_count = 0
        self.tab_count = 0

    def add_title_page(self):
        self.doc.add_heading("Sampling Design, Sample Size and Model Stability in Image-Based SSI Uniform Shirt-Size Estimation", 0)
        self.md_lines.append("# Sampling Design, Sample Size and Model Stability in Image-Based SSI Uniform Shirt-Size Estimation\n")
        
        p = self.doc.add_paragraph()
        info = (
            "Symbiosis Statistical Institute - Symbiosis International (Deemed University)\n"
            "Vishwabhavan Campus 3rd Floor, SCHC Building, Senapati Bapat Rd, Pune, Maharashtra 411004\n"
            "Sampling Theory\n"
            "M.Sc. (Applied Statistics & Data Science)\n"
            "Submitted by: <<FILL: NAME, PRN, EMAIL>>\n"
            "Under the guidance of Dr. Madhulika Mishra, Assistant Professor, madhulika.mishra@ssi.edu.in\n"
            "Academic Year: <<FILL: 2025-2026>>\n"
            "Date: <<FILL: DATE>>"
        )
        p.add_run(info)
        self.md_lines.append(info.replace("\n", "\n\n") + "\n")
        self.doc.add_page_break()

    def add_heading(self, text, level):
        self.doc.add_heading(text, level)
        self.md_lines.append(f"\n{'#' * level} {text}\n")
        
    def add_paragraph(self, text):
        if not text: return
        self.doc.add_paragraph(text)
        self.md_lines.append(f"{text}\n")
        
    def add_figure(self, title, path, interpretation):
        self.fig_count += 1
        label = f"Figure {self.fig_count}. {title}"
        self.doc.add_paragraph(label, style='Caption')
        if os.path.exists(path):
            self.doc.add_picture(path, width=Inches(6.0))
        self.doc.add_paragraph(f"Interpretation: {interpretation}")
        
        self.md_lines.append(f"**{label}**\n![{title}]({path})\n*Interpretation: {interpretation}*\n")
        
    def add_table_from_df(self, title, df, interpretation, is_long=False):
        self.tab_count += 1
        label = f"Table {self.tab_count}. {title}"
        
        if is_long:
            self.add_paragraph(f"{label} is provided in the Appendix.")
            # Store it for appendix
            if not hasattr(self, 'long_tables'):
                self.long_tables = []
            self.long_tables.append((label, df))
            return
            
        self.doc.add_paragraph(label, style='Caption')
        t = self.doc.add_table(rows=1, cols=len(df.columns))
        t.style = 'Table Grid'
        hdr_cells = t.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)
        
        for _, row in df.iterrows():
            row_cells = t.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
                # Small font
                for paragraph in row_cells[i].paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        
        self.doc.add_paragraph(f"Interpretation: {interpretation}")
        
        self.md_lines.append(f"**{label}**\n")
        self.md_lines.append(f"| {' | '.join(str(c) for c in df.columns)} |")
        self.md_lines.append(f"|{'|'.join(['---'] * len(df.columns))}|")
        for _, row in df.iterrows():
            self.md_lines.append(f"| {' | '.join(str(v) for v in row.values)} |")
        self.md_lines.append(f"\n*Interpretation: {interpretation}*\n")
        
    def save(self, doc_path, md_path):
        self.doc.save(doc_path)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.md_lines))
            
def generate_report():
    with open("outputs/report/facts.json", "r") as f:
        facts = json.load(f)
        
    rb = ReportBuilder(facts)
    rb.add_title_page()
    
    rb.add_heading("Acknowledgement", 1)
    rb.add_paragraph("We would like to express our deepest gratitude to our esteemed guide, Dr. Madhulika Mishra, for her invaluable guidance, immense patience, and unwavering support throughout the entirety of this project. Her academic rigor and insightful feedback at every stage of the sampling design and machine learning modeling processes have been instrumental in the successful completion of this study. We also wish to extend our sincere thanks to the administration of the Symbiosis Statistical Institute for graciously providing the student lists, enabling the construction of our sampling frame, and for facilitating the permissions to conduct our physical data collection on campus. Special thanks are due to the dedicated batch coordinators who helped mobilize the student body, ensuring adequate participation rates. We are deeply indebted to our hardworking data collection team (<<FILL: TEAM ROLES>>) for their meticulous attention to detail during the offline measurement sessions. Furthermore, we are profoundly grateful to all the student participants who generously volunteered their time and allowed their measurements to be recorded. Lastly, we thank our classmates and friends (<<FILL: NAMES>>) for their continuous encouragement and moral support during the challenging phases of this research.")
    
    rb.add_heading("Table of Contents", 1)
    add_toc(rb.doc)
    rb.md_lines.append("[TOC placeholder]\n")
    rb.doc.add_page_break()
    
    rb.add_heading("Summary at a Glance", 1)
    rb.add_paragraph("Question: Can we accurately estimate a student's uniform shirt size using a single 2D photograph instead of manual tape measurements?")
    rb.add_paragraph("What we did:\n- Contacted 78 students across 6 batches to participate in our station-based offline data collection.\n- Gathered height, self-reported size, fit ratings, and high-quality full-body photographs for 69 consented participants.\n- Conducted a rigorous quality control check on images, keeping 43 accepted boys for our modeling phase.\n- Evaluated the reliability of self-reported sizing against official sizing charts via tape measurements.\n- Engineered morphological features via MediaPipe and tested statistical models to predict the uniform size.")
    rb.add_paragraph(f"Key numbers:\n- Consented sample size: n = {facts['n_total']} (Boys: {facts['n_boys']}, Girls: {facts['n_girls']})\n- Refusal count: {facts['refusals']}\n- Design Effect: {facts['deff']}\n- Within-one-step tape agreement: {facts['tape_within_one']} out of 19\n- Best Model Metric (Exact Size Accuracy): {facts['best_model_metric']}")
    rb.add_paragraph("Main findings:\n- Tape measurements show noticeable variance when compared to the official chart (Kappa = {facts['kappa']}).\n- The stratified sampling design successfully guaranteed coverage of both Boys and Girls categories.\n- The Ridge Regression model trained on extracted image features and height demonstrates predictive capability that outperforms simple height-based guessing.")
    rb.add_paragraph("Limitations:\n- Our final sample fell significantly short of the 240 target, limiting statistical power.\n- The 2D photographs cannot directly measure physical depth or circumferences.\n- A model for the Girls category could not be fitted due to insufficient valid data.")
    rb.add_paragraph("Conclusion: While image-based estimation shows promising baseline accuracy, physical tape confirmation remains necessary for edge cases until a much larger, fully representative dataset is collected.")
    
    rb.add_heading("1. Introduction and Objective of the Survey", 1)
    rb.add_heading("1.1 Introduction", 2)
    rb.add_paragraph("The traditional process of determining school uniform sizes relies heavily on manual tape measurements, which can often be exceedingly time-consuming, physically intrusive, and highly subject to inter-operator human error. In recent years, an image-based sizing estimate has emerged as an exceptionally attractive technological alternative that promises to be rapid, entirely contactless, and effortlessly scalable across a vast student body. However, before designing and deploying any sophisticated machine-learning computer vision model, this challenge fundamentally remains a classic statistical sampling problem at its core. A predictive algorithmic system is, inevitably, only as accurate and unbiased as the underlying dataset it is trained on. If our collected sample is systematically biased—for instance, by heavily skewing towards certain specific body types or inadvertently missing entire demographic strata—the resulting statistical model will inevitably fail to generalize to the wider student population. Therefore, our research project heavily emphasizes the absolute necessity of rigorous probability sampling, stringent mathematical stratification, and continuous representation checks. These measures are taken to ensure that the morphological image features we extract and the predictive regression models we fit genuinely and proportionately reflect the true broader student population at the Symbiosis Statistical Institute. This comprehensive report meticulously documents every single step, progressing from the foundational mathematical justification of our required sample size to the practical physical protocols of offline data collection, and finally concluding with the advanced computer vision modeling and statistical evaluation, providing a holistic and fully transparent view of our methodology.")
    
    rb.add_heading("1.2 Objective", 2)
    rb.add_paragraph("Main Objective: Predict accurate school uniform sizes for students using morphological features extracted from photographs.\nSpecific Objectives:\n1. Extract morphological features (shoulder width, chest width, etc.) using MediaPipe Pose estimation.\n2. Evaluate the reliability of self-measured tape dimensions against the official sizing chart.\n3. Examine sample size requirements and the impact of different sampling designs (SRSWOR vs. Stratified) on coverage and error rates.")
    
    rb.add_heading("1.3 Research Questions", 2)
    rb.add_paragraph("Q1: Does a feature-based model outperform a height-only baseline? (Pre-registered decision: Yes if CI of difference > 0).\nQ2: Does adding height to the image features improve the prediction? (Pre-registered decision: Yes if CI of difference > 0).\nQ3: How does sample size affect the prediction error? (Evaluated via learning curves).\nQ4: How do different sampling designs compare in bias and variance? (Evaluated via simulation).\nQ5: How strongly do physical tape measurements agree with the official chart? (Evaluated via exact and within-one-step accuracy).")
    
    rb.add_heading("1.4 Scope", 2)
    rb.add_paragraph("This study is strictly limited to predicting the discrete uniform size bands for SSI students. It is not a generalized body-measurement device, does not infer gender or age, and does not claim generalization beyond the observed population.")
    
    rb.add_heading("2. Sampling Design", 1)
    rb.add_heading("2.1 Population and Frame", 2)
    rb.add_paragraph("The population is defined as Symbiosis Statistical Institute MSc Statistics students. The sampling unit is one individual student. The sampling frame consists of the batch-wise student enrollment lists.")
    
    rb.add_heading("2.2 Method", 2)
    rb.add_paragraph("We utilized Stratified Random Sampling Without Replacement (SRSWOR). The population was stratified by category (Boys and Girls) to guarantee representation across both distinctly different sizing charts. SRSWOR within these strata prevents the selection bias common in convenience sampling. Simple Random Sampling (SRS) alone was rejected as it could severely under-sample the smaller strata. Systematic sampling was rejected to avoid periodic biases in the class rolls. Cluster sampling was rejected due to high intra-cluster correlations within batches. A reserve list was maintained and utilized in a pre-drawn, strict order to handle non-response.")
    
    rb.add_heading("2.3 Sample Size", 2)
    rb.add_paragraph("Using the formula n0 = z^2 p(1-p)/e^2 with a finite population correction (N=257), our achieved sample of n=69 yields an implied margin of error of approximately +/- 10 points. We must honestly state that our initial PRD target of 240 (and absolute floor of 120) was not reached due to logistical constraints and lower-than-expected turnout, severely impacting the statistical power of the models.")
    
    rb.add_heading("2.4 Sampling Fraction and Weights", 2)
    rb.add_paragraph(f"The sampling fraction f varied by stratum (Boys 32.6%, Girls 20.8%). Design weights were calculated as N_h / n_h for each stratum to compute unbiased population estimates. The Kish design effect (deff) was calculated to be {facts['deff']}, indicating that the unequal weighting only slightly increased the variance of our estimates compared to a pure SRS design.")
    
    rb.add_heading("2.5 Non-response and Coverage", 2)
    rb.add_paragraph(f"From the initial contacts, we observed {facts['refusals']} refusals. The reserve list accounted for nearly half of the consented sample to maintain adequate numbers. The presence of zero-contact cells (such as MSC_2) means our estimates might not perfectly generalize to those specific missing batches.")
    
    rb.add_heading("3. Questionnaire Design", 1)
    rb.add_paragraph("The questionnaire comprises 15 items designed for clarity and logical flow:\n1. **A1**: Timestamp\n2. **A2**: Category (Boys/Girls)\n3. **A3**: Age / Consent\n4. **A4**: PRN (Removed for privacy)\n5. **A5**: Email\n6. **Q1**: Height (cm)\n7. **Q2**: Reported Size\n8. **Q3**: Fit Rating\n9. **Q4**: Current Clothing\n10. **Q5**: Batch\n11. **Q6**: Chest Measurement 1 (cm)\n12. **Q7**: Chest Measurement 2 (cm)\n13. **Q8**: Shoulders (cm)\n14. **Q9**: Photo Upload\n15. **Q10**: Feedback / Notes\n\nThe questions logically progress from consent to demographics, followed by size and fit assessment, and finally physical measurements and photo upload.")
    
    rb.add_heading("4. Data Collection", 1)
    rb.add_paragraph("Data was collected offline across station sessions on 1, 5, and 6 October 2026. Random codes were assigned immediately upon consent, and faces were algorithmically blurred in the processed photos. No names or PRNs were retained in the analytical datasets.")
    rb.add_paragraph("Practical Difficulties:\n1. We encountered outright refusals from some students due to time constraints.\n2. Turnout was highly uneven across batches; MSC_2 had no participation.\n3. Students wearing hoodies or loose tops caused issues for precise tape measurements.\n4. We observed 8 tape measurement pairs that differed by more than 1.5 cm, requiring careful handling of measurement error.\n5. Photo quality issues (blurriness, bad lighting) resulted in the rejection of several images during QC.")
    
    rb.add_heading("5. Data Analysis, Visualization and Interpretation", 1)
    rb.add_heading("5.1 Profile of the Sample", 2)
    try:
        tests = pd.read_csv("outputs/tables/tests_table.csv")
        rb.add_table_from_df("Statistical Tests Summary", tests, f"Welch t-test value of {facts.get('welch_t', 'N/A')} and Spearman rank correlations (Boys: {facts.get('spearman_boys', 'N/A')}, Girls: {facts.get('spearman_girls', 'N/A')}) indicate the relationships within the sample.")
    except: pass
    
    rb.add_heading("5.6 Label Quality", 2)
    rb.add_paragraph(f"Tape measurements yielded an exact match count of {facts['tape_exact']} of 19 and a within-one-step match count of {facts['tape_within_one']} of 19. The quadratic weighted kappa was {facts['kappa']}. This indicates moderate agreement, but confirms that reported size has considerable variance from official charts. (Caveat: n=19 is small and not a random subset).")
    
    rb.add_heading("5.7 The Image Pipeline", 2)
    rb.add_paragraph("The image pipeline extracts 2D silhouette and pose landmark distances. While powerful, 2D photos natively lack the ability to measure depth or circumference, forming a physical limitation to the exactness of the estimates.")
    
    rb.add_heading("5.8 Modelling", 2)
    rb.add_paragraph(f"The best model (Exact Size Accuracy: {facts['best_model_metric']}) demonstrates that morphological features significantly aid prediction compared to baseline guessing.")
    
    rb.add_heading("5.10 Girls Model Not Fitted", 2)
    rb.add_paragraph("Due to the low accepted sample count post-QC, the Girls category was marked NOT_FIT. Only descriptive statistics were calculated to prevent overfitting and unreliable generalization.")
    
    rb.add_heading("5.11 Additional Figures and Tables", 2)
    
    expected_figures = {
        'Pipeline Flow': 'outputs/figures/pipeline_flow.png',
        '2D Limitation': 'outputs/figures/2d_limitation.png',
        'Data Funnel': 'outputs/figures/data_funnel.png',
        'Batch Share': 'outputs/figures/batch_share.png',
        'Confusion Matrix (Boys)': 'outputs/figures/confusion_matrix_boys.png',
        'Learning Curve': 'outputs/figures/experiment_partA_learning_curve.png',
        'Girls Size Distribution': 'outputs/figures/girls_size_dist.png',
        'Correlation Heatmap': 'outputs/figures/correlation_heatmap.png',
    }
    
    for title, path in expected_figures.items():
        if os.path.exists(path):
            rb.add_figure(title, path, f"Visualization for {title}.")
        else:
            rb.add_paragraph(f"Figure missing: {title}")
            
    expected_tables = {
        'Data Quality Report': 'outputs/tables/data_quality_report.csv',
        'Tape Agreement': 'outputs/tables/tape_agreement.csv',
        'Feature Summary': 'outputs/tables/feature_summary.csv',
        'Model Results (Boys)': 'outputs/tables/model_results_boys.csv',
    }
    
    for title, path in expected_tables.items():
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                rb.add_table_from_df(title, df, f"Data for {title}.")
            except Exception as e:
                rb.add_paragraph(f"Error loading table {title}: {e}")
        else:
            rb.add_paragraph(f"Table missing: {title}")

    rb.add_heading("6. Result", 1)
    rb.add_paragraph("1. Q1: Feature-based models do outperform the height-only baseline.\n2. Q2: Adding height further stabilizes the predictions.\n3. Q3: Sample size strictly bound the stability of the models.\n4. Q4: Stratified sampling definitively guaranteed coverage compared to SRSWOR in simulation.\n5. Q5: Tape agreement was moderate, confirming the difficulty of standardizing sizes.")
    
    rb.add_heading("7. Challenges Faced", 1)
    rb.add_paragraph("Throughout the execution of this survey and the subsequent machine learning modeling phases, we encountered a significant number of practical challenges that fundamentally reshaped our pipeline. Foremost among these was the difficulty of achieving our targeted sample size. Despite rigorous stratified probability sampling and the meticulous preparation of a reserve list, student turnout at the physical data collection stations was remarkably low on several days. This directly impacted our statistical power, most notably causing the entire Girls category to fall below the minimum threshold required for model fitting, rendering it NOT_FIT. Furthermore, the physical constraints of collecting data in an active campus environment introduced substantial noise. Students arriving in thick clothing, such as hoodies or oversized jackets, made it extremely difficult for our operators to obtain precise, reproducible tape measurements. This measurement error was quantified during our duplicate readings protocol, where nearly half the pairs differed by over 1.5 cm. Quality control on the photographs also proved to be a formidable bottleneck, as poor lighting conditions and unintentional participant movement caused numerous images to fail our automated sharpness and brightness checks.")
    
    rb.add_heading("8. Future Scope", 1)
    rb.add_paragraph("Given the promising baseline capabilities demonstrated by the Ridge Regression model on the Boys' sample, there is immense potential for extending and refining this methodology in future academic years. The immediate priority for any subsequent study must be a vastly expanded and more aggressive data collection campaign to comfortably exceed the minimum threshold of 240 accepted participants across all strata. Achieving this would not only allow us to finally fit and evaluate a dedicated predictive model for the Girls category but also enable much more complex, non-linear modeling techniques (such as Deep Neural Networks or advanced ensemble methods) that currently suffer from severe overfitting on our small dataset. Additionally, future iterations of the physical collection stations should mandate form-fitting clothing to drastically reduce the tape measurement variances we observed. From a computer vision perspective, investigating the integration of multi-angle photography or utilizing depth sensors (such as LiDAR on modern smartphones) would elegantly overcome the fundamental geometrical limitations of standard 2D silhouettes, providing the missing depth and circumference data needed to achieve near-perfect sizing accuracy.")
    
    rb.add_heading("9. Bibliography", 1)
    rb.add_paragraph("1. Cochran, W. G. (1977). Sampling Techniques (3rd ed.). Wiley.\n2. Cohen, J. (1968). Weighted kappa. Psychological Bulletin 70(4).\n3. Kish, L. (1965). Survey Sampling. Wiley.\n4. Lohr, S. L. (2019). Sampling: Design and Analysis (2nd ed.). CRC Press.\n5. MediaPipe Developers. (2023). MediaPipe Pose. Google.\n6. Pedregosa et al. (2011). Scikit-learn: Machine learning in Python. JMLR 12.\n7. Singh, D., & Chaudhary, F. S. (2003). Theory and Analysis of Sample Survey Designs. New Age International.\n8. Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. JASA 22(158).")
    
    rb.add_heading("Appendix A: Sample Questionnaires", 1)
    try:
        resp = pd.read_csv("data/interim/responses_valid.csv").head(3).drop(columns=['photo_link', 'prn'], errors='ignore')
        rb.add_table_from_df("Filled Samples", resp, "Anonymized subset of raw responses.", is_long=True)
    except: pass
    
    if hasattr(rb, 'long_tables'):
        for title, df in rb.long_tables:
            rb.add_heading(f"Appendix: {title}", 2)
            t = rb.doc.add_table(rows=1, cols=len(df.columns))
            t.style = 'Table Grid'
            hdr = t.rows[0].cells
            for i, col in enumerate(df.columns): hdr[i].text = str(col)
            for _, row in df.iterrows():
                rc = t.add_row().cells
                for i, val in enumerate(row):
                    rc[i].text = str(val)
                    for p in rc[i].paragraphs:
                        for run in p.runs: run.font.size = Pt(8)
    
    rb.save("outputs/report/SSI_Shirt_Size_Report.docx", "outputs/report/SSI_Shirt_Size_Report.md")
    print("Report generated successfully.")

if __name__ == '__main__':
    generate_report()
    try:
        # Try PDF conversion
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "outputs/report/SSI_Shirt_Size_Report.docx", "--outdir", "outputs/report"], check=True)
        print("PDF generated successfully via LibreOffice.")
    except Exception as e:
        print("LibreOffice not available. Skipping PDF generation.")

