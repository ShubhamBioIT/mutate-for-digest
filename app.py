import streamlit as st
import re
import io
import base64
from typing import List, Tuple
import pandas as pd
from datetime import datetime
import re as _re
import requests


# Set page config
st.set_page_config(
    page_title="Mutate for Digest - Bioinformatics Tool",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a reset button using Streamlit session state
def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]

if "reset" not in st.session_state:
    st.session_state["reset"] = False

if st.sidebar.button("🔄 Reset Page"):
    reset_app()
    st.rerun()

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .feature-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-weight: 500;
    }
    
    .result-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000000;
        font-family: 'Courier New', monospace;
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #000000;
        border-left: 4px solid #38a169;
        font-weight: 500;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #000000;
        border-left: 4px solid #ed8936;
        font-weight: 500;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        min-width: 150px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .dna-sequence {
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.5;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #dee2e6;
        word-break: break-all;
    }
    
    .restriction-site {
        background-color: #fff3cd;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-weight: bold;
        color: #856404;
    }
    
    .mutation-highlight {
        background-color: #f8d7da;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        font-weight: bold;
        color: #721c24;
    }

    .stTextArea textarea {
        font-family: 'Courier New', monospace;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Core bioinformatics functions (from your main.py)
def right_num(number, filler, width, suffix):
    if filler == "":
        filler = " "
    return str(int(number)).rjust(width, filler) + suffix

def convert_degenerates(seq: str) -> str:
    degenerates = {
        'N': '[ACGT]', 'R': '[AG]', 'Y': '[CT]', 'S': '[GC]',
        'W': '[AT]', 'K': '[GT]', 'M': '[AC]', 'B': '[CGT]',
        'D': '[AGT]', 'H': '[ACT]', 'V': '[ACG]'
    }
    pattern = ''
    for char in seq.upper():
        pattern += degenerates.get(char, char)
    return pattern

class RestrictionSite:
    def __init__(self, label: str, position: int, cut_distance: int, iupac_pattern: str):
        self.label = label
        self.position = position
        self.cut_distance = cut_distance
        self.iupac_pattern = iupac_pattern
        self.number_of_cuts = 0

class RestrictionSiteCollection:
    def __init__(self):
        self.restriction_sites: List[RestrictionSite] = []

    def add_restriction_site(self, restriction_site: RestrictionSite):
        self.restriction_sites.append(restriction_site)

    def sort_restriction_sites(self):
        self.restriction_sites.sort(key=lambda x: -x.position)

def translate_dna(dna_sequence: str, genetic_code_dict: dict) -> str:
    """Translate DNA sequence to amino acids"""
    clean_dna = re.sub(r'[^A-Za-z]', '', dna_sequence.upper())
    if len(clean_dna) < 3:
        return ""
    
    amino_acids = []
    for i in range(0, len(clean_dna) - 2, 3):
        codon = clean_dna[i:i+3]
        amino_acid = genetic_code_dict.get(codon, 'X')
        amino_acids.append(amino_acid)
    
    return ''.join(amino_acids)

def build_mutated_restriction_sites(restriction_sites: List[str]) -> List[str]:
    mutated_sites = []
    for site in restriction_sites:
        match = re.search(r'/([^/]+)/', site)
        pattern = match.group(1).lower() if match else ''
        label = re.search(r'\([^\(]+\)', site).group(0)
        cut_distance = float(re.search(r'\)\D*(\d+)', site).group(1))

        single_degen = []
        double_degen = []

        for i in range(len(pattern)):
            if pattern[i] not in ('n', 'N'):
                single_degen.append(pattern[:i] + 'N' + pattern[i+1:])

        if len(pattern) > 6:
            for item in single_degen:
                for j in range(len(item)):
                    if item[j] not in ('n', 'N'):
                        double_degen.append(item[:j] + 'N' + item[j+1:])

        for s in single_degen + double_degen:
            mutated_sites.append(f"/{s}/ {label}{cut_distance}")

    return mutated_sites

def find_restriction_sites(sequence: str, items: List[str], conformation: str) -> RestrictionSiteCollection:
    look_ahead = 50
    lower_limit = 0
    upper_limit = len(sequence)
    shift_value = 0
    collection = RestrictionSiteCollection()

    if conformation == "circular":
        shift_value = len(sequence[:look_ahead])
        sequence = sequence[-look_ahead:] + sequence + sequence[:look_ahead]
        lower_limit += shift_value
        upper_limit += shift_value

    for item in items:
        iupac_pattern = re.search(r'/([^/]+)/', item).group(1)
        match_exp = re.compile(convert_degenerates(iupac_pattern), re.IGNORECASE)
        cut_distance = int(re.search(r'\)\D*(\d+)', item).group(1))
        label = re.search(r'\([^\(]+\)', item).group(0)[1:-1]

        matches = list(match_exp.finditer(sequence))

        for match in matches:
            pos = match.start() - cut_distance
            if lower_limit <= pos < upper_limit:
                collection.add_restriction_site(
                    RestrictionSite(f"{label} at position {pos - shift_value + 1}", 
                                  pos - shift_value, cut_distance, iupac_pattern)
                )

    return collection

# Streamlit App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧬 Mutate for Digest</h1>
        <h3>Bioinformatics Tool For Restriction Site & Mutation Analysis </h3>
        <p>Find restriction enzyme sites in your DNA, and see what small changes could add new sites. Check how these changes affect the protein.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("## 🔧 Configuration")
    
    # Sample files download
    st.sidebar.markdown("### 📥 Download Sample Files")
    
    
    sample_dna = """>CDS1
atgtctgattcgctaaatcatccatcgagttctacggtgcatgcagatgatggattcgag
ccaccaacatctccggaagacaacaacaaaaaaccgtctttagaacaaattaaacaggaa
agagaagcgttgtttacggatctattcgcagatcgtcgacgaagcgctcgttctgtgatt
gaagaagctttccaaaacgaactcatgagtgctgaaccagtccagccaaacgtgccgaat
ccacattcgattcccattcgtttccgtcatcaaccagttgctggacctgctcatgatgtt
ttcggagacgcggtgcattcaatttttcaaaaaataatgtccagaggagtgaacgcggat
tatagtcattggatgtcatattggatcgcgttgggaatcgacaaaaaaacacaaatgaac
tatcatatgaaaccgttttgcaaagatacttatgcaactgaaggctccttagaagcgaaa
caaacatttactgataaaatcaggtcagctgttgaggaaattatctggaagtccgctgaa
tattgtgatattcttagcgagaagtggacaggaattcatgtgtcggccgaccaactgaaa
ggtcaaagaaataagcaagaagatcgttttgtggcttatccaaatggacaatacatgaat
cgtggacagagtgacatttcacttcttgcggtgttcgatgggcatggcggacacgagtgc
tctcaatatgcagctgctcatttctgggaagcatggtccgatgctcaacatcatcattca
caagatatgaaacttgacgaactcctagaaaaggctctagaaacattggacgaaagaatg
acagtcagaagtgttcgagaatcttggaaaggtggaaccactgctgtctgctgtgctgtt
gatttgaacactaatcaaatcgcatttgcctggcttggagattcaccaggttacatcatg
tcaaacttggagttccgcaaattcactactgaacactccccgtctgacccggaggaatgt
cgacgagtcgaagaagtcggtggccagatttttgtgatcggtggtgagctccgtgtgaat
ggagtactcaacctgacgcgagcactaggagacgtacctggaagaccaatgatatccaac
aaacctgataccttactgaagacgatcgaacctgcggattatcttgttttgttggcctgt
gacgggatttctgacgtcttcaacactagtgatttgtacaatttggttcaggcttttgtc
aatgaatatgacgtagaagattatcacgaacttgcacgctacatttgcaatcaagcagtt
tcagctggaagtgctgacaatgtgacagtagttataggtttcctccgtccaccagaagac
gtttggcgtgtaatgaaaacagactcggatgatgaagagagcgagctcgaggaagaagat
gacaatgaatag"""


    if st.sidebar.button("📄 Download Sample DNA"):
        st.sidebar.download_button(
            label="💾 Download DNA FASTA",
            data=sample_dna,
            file_name="sample_dna.fasta",
            mime="text/plain"
        )
    
    # Comprehensive restriction enzyme database
    restriction_enzymes_db = {
        "EcoRI": "/GAATTC/ (EcoRI)1",
        "BamHI": "/GGATCC/ (BamHI)1", 
        "HindIII": "/AAGCTT/ (HindIII)1",
        "PstI": "/CTGCAG/ (PstI)1",
        "SalI": "/GTCGAC/ (SalI)1",
        "XbaI": "/TCTAGA/ (XbaI)1",
        "SacI": "/GAGCTC/ (SacI)1",
        "KpnI": "/GGTACC/ (KpnI)1",
        "SmaI": "/CCCGGG/ (SmaI)3",
        "XhoI": "/CTCGAG/ (XhoI)1",
        "NotI": "/GCGGCCGC/ (NotI)2",
        "ApaI": "/GGGCCC/ (ApaI)1",
        "BglII": "/AGATCT/ (BglII)1",
        "ClaI": "/ATCGAT/ (ClaI)2",
        "DraI": "/TTTAAA/ (DraI)3",
        "EcoRV": "/GATATC/ (EcoRV)3",
        "HaeII": "/RGCGCY/ (HaeII)3",
        "HpaI": "/GTTAAC/ (HpaI)3",
        "MluI": "/ACGCGT/ (MluI)1",
        "NcoI": "/CCATGG/ (NcoI)1",
        "NdeI": "/CATATG/ (NdeI)2",
        "NheI": "/GCTAGC/ (NheI)1",
        "NruI": "/TCGCGA/ (NruI)3",
        "PvuII": "/CAGCTG/ (PvuII)3",
        "ScaI": "/AGTACT/ (ScaI)3",
        "SpeI": "/ACTAGT/ (SpeI)1",
        "SphI": "/GCATGC/ (SphI)1",
        "StuI": "/AGGCCT/ (StuI)3",
        "TaqI": "/TCGA/ (TaqI)1",
        "XmaI": "/CCCGGG/ (XmaI)1",
        "AseI": "/ATTAAT/ (AseI)3",
        "AvrII": "/CCTAGG/ (AvrII)1",
        "BspEI": "/TCCGGA/ (BspEI)1",
        "BssHII": "/GCGCGC/ (BssHII)1",
        "BstXI": "/CCANNNNNNTGG/ (BstXI)8",
        "EagI": "/CGGCCG/ (EagI)1",
        "FseI": "/GGCCGGCC/ (FseI)6",
        "PacI": "/TTAATTAA/ (PacI)5",
        "PmeI": "/GTTTAAAC/ (PmeI)4",
        "SbfI": "/CCTGCAGG/ (SbfI)6",
        "SgrAI": "/CRCCGGYG/ (SgrAI)2",
        "SrfI": "/GCCCGGGC/ (SrfI)4",
        "SwaI": "/ATTTAAAT/ (SwaI)4",
        "AflII": "/CTTAAG/ (AflII)1",
        "AgeI": "/ACCGGT/ (AgeI)1",
        "AlwNI": "/CAGNNNCTG/ (AlwNI)6",
        "BsiWI": "/CGTACG/ (BsiWI)1",
        "BspHI": "/TCATGA/ (BspHI)1",
        "Eco53kI": "/GAGCTC/ (Eco53kI)3",
        "HincII": "/GTYRAC/ (HincII)3",
        "MscI": "/TGGCCA/ (MscI)3",
        "PflMI": "/CCANNNNNTGG/ (PflMI)7",
        "PshAI": "/GACNNNNGTC/ (PshAI)5",
        "PvuI": "/CGATCG/ (PvuI)4",
        "SacII": "/CCGCGG/ (SacII)4"
    }

    # Parameters
    st.sidebar.markdown("### ⚙️ Analysis Parameters")
    topology = st.sidebar.selectbox("DNA Topology", ["linear", "circular"], help="Choose DNA conformation")
    bases_per_line = st.sidebar.slider("Bases per line", 30, 120, 60, help="Number of bases to display per line")
    reading_frame = st.sidebar.multiselect(
        "Reading Frame(s)",
        ["1", "2", "3"],
        default=["1"],
        help="Select one or more translation reading frames"
    )
    if not reading_frame:
        st.sidebar.warning("Please select at least one reading frame.")
    
    # Restriction enzyme selection
    st.sidebar.markdown("### 🔬 Restriction Enzyme Selection")
    
    # Option to use custom enzymes or select from database
    enzyme_input_method = st.sidebar.radio("Choose enzyme input method:", 
                                         ["Select from Database", "Custom Input"])
    
    restriction_sites_list = []
    
    if enzyme_input_method == "Select from Database":
        selected_enzymes = st.sidebar.multiselect(
            "Select restriction enzymes:",
            options=list(restriction_enzymes_db.keys()),
            default=["EcoRI", "BamHI", "HindIII"],
            help="Choose from common restriction enzymes"
        )
        
        if selected_enzymes:
            restriction_sites_list = [restriction_enzymes_db[enzyme] for enzyme in selected_enzymes]
            
        # Display selected enzymes
        if restriction_sites_list:
            st.sidebar.markdown("**Selected Enzymes:**")
            for enzyme in selected_enzymes:
                pattern = restriction_enzymes_db[enzyme].split('(')[0].strip('/')
                st.sidebar.write(f"• {enzyme}: {pattern}")
    else:
        # Custom input (will be handled in main content area)
        pass

    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🧬 DNA Sequence Input")
        
        # Input method selection
        input_method = st.radio("Choose input method:", ["Text Input", "File Upload"])
        
        dna_input = ""
        if input_method == "Text Input":
            dna_input = st.text_area(
                "Enter DNA sequence (FASTA format):",
                height=200,
                placeholder=">Your_Sequence_Name\nATGCGTACGTAGCTAGCTAG...",
                help="Enter your DNA sequence in FASTA format"
            )
        else:
            uploaded_file = st.file_uploader("Upload FASTA file", type=['fasta', 'fa', 'txt'])
            if uploaded_file:
                dna_input = uploaded_file.read().decode('utf-8')
                st.text_area("Uploaded sequence:", dna_input, height=100, disabled=True)

        st.markdown("## 🔬 Restriction Sites")
        
        if enzyme_input_method == "Custom Input":
            restriction_sites_input = st.text_area(
                "Enter restriction sites (one per line):",
                value="""/GAATTC/ (EcoRI)1
/AAGCTT/ (HindIII)1
/GGATCC/ (BamHI)1""",
                height=150,
                help="Format: /PATTERN/ (Name)CutDistance"
            )
            restriction_sites_list = [site.strip() for site in restriction_sites_input.split('\n') if site.strip()]
        else:
            # Show selected enzymes from database
            if restriction_sites_list:
                st.success(f"✅ Selected {len(restriction_sites_list)} restriction enzymes from database")
                
                # Display in a nice format
                enzyme_display = "\n".join([f"• {site.split('(')[1].split(')')[0]}: {site.split('(')[0].strip('/')}" 
                                          for site in restriction_sites_list])
                st.markdown(f"""
                <div class="info-box">
                    <h4>🧬 Selected Restriction Enzymes:</h4>
                    <pre>{enzyme_display}</pre>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please select at least one restriction enzyme from the sidebar!")

    with col2:
        st.markdown("## ℹ️ Information")
        
        st.markdown("""
        <div class="info-box" style="max-height: 300px; overflow-y: auto;">
            <h4>🧬 How This Tool Works (Step by Step)</h4>
            <ol style="padding-left: 1.2em;">
            <li><b>Input DNA Sequence:</b> Paste or upload your DNA sequence in FASTA format. The tool will clean and process your input automatically.</li>
            <li><b>Select Restriction Enzymes:</b> Choose enzymes from the database or enter custom recognition patterns. Each enzyme has a specific DNA sequence it recognizes and cuts.</li>
            <li><b>Scan for Sites:</b> The tool searches your DNA for exact matches to the selected restriction sites and shows their positions.</li>
            <li><b>Suggest Mutations:</b> If a restriction site is not present, the tool finds places where a small change (mutation) could create a new site. It suggests which bases to change and highlights if this would also change the protein sequence.</li>
            <li><b>Protein Translation:</b> The DNA is translated into its protein sequence (amino acids) in your chosen reading frame. If a suggested mutation changes the protein, this is clearly shown.</li>
            <li><b>Visual Results:</b> All results are shown in tables and color-coded sequence views. You can see where enzymes cut, where mutations could help, and how the protein is affected.</li>
            <li><b>Interactive Sequence Visualization:</b> The DNA sequence is displayed with color-coded nucleotides. Restriction enzyme cut sites are highlighted and labeled directly above the affected bases, making it easy to spot where each enzyme acts. Mutations that introduce new sites are also visually marked, and amino acid changes are highlighted in the protein translation view.</li>
            <li><b>Download Everything:</b> All results, including tables and sequences, can be downloaded for your records or further analysis.</li>
            </ol>
            <p style="font-size: 0.95em; color: #222;">
            <b>Tip:</b> This tool is designed to help with cloning, mutagenesis, and synthetic biology. It makes it easy to plan restriction digests and check the impact of introducing new sites.<br>
            <b>Visual Guide:</b> Colored letters represent nucleotides (A, T, G, C). Enzyme names appear above cut sites, and highlighted backgrounds show where mutations or amino acid changes occur.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Input Format:</h4>
            <p><strong>DNA:</strong> FASTA format with header</p>
            <p><strong>Sites:</strong> /PATTERN/ (Name)Distance</p>
        </div>
        """, unsafe_allow_html=True)

    # Analysis button
    if st.button("🚀 Analyze Sequence", type="primary", use_container_width=True):
        if dna_input and restriction_sites_list:
            with st.spinner("Analyzing DNA sequence..."):
                # Process input
                dna_sequences = [dna_input.strip()]
                
                # Genetic code dictionary
                genetic_code_dict = {
                    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
                    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
                    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
                    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
                    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
                    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
                    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
                    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
                    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
                    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
                    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
                    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
                    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
                    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
                    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
                    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
                }
                
                # Process each sequence
                for fasta in dna_sequences:
                    lines = fasta.strip().split('\n')
                    title = lines[0][1:] if lines[0].startswith('>') else "Untitled"
                    new_dna = ''.join(lines[1:])
                    new_dna = re.sub(r'[^acgtACGT]', '', new_dna)
                    
                    if not new_dna:
                        st.error("No valid DNA sequence found!")
                        return
                    
                    # Display results header
                    st.markdown("## 📊 Analysis Results")
                    
                    # Sequence statistics
                    gc_content = (new_dna.upper().count('G') + new_dna.upper().count('C')) / len(new_dna) * 100
                    
                    st.markdown(f"""
                    <div class="stats-container" style="color: #222; font-family: 'Segoe UI', 'Arial', sans-serif;">
                        <div class="stat-box" style="color: #222;">
                            <h3 style="color: #222; font-weight: 700; font-family: 'Segoe UI', 'Arial', sans-serif;">{len(new_dna)}</h3>
                            <p style="color: #444; font-size: 1.1em; font-family: 'Segoe UI', 'Arial', sans-serif;">Base Pairs</p>
                        </div>
                        <div class="stat-box" style="color: #222;">
                            <h3 style="color: #222; font-weight: 700; font-family: 'Segoe UI', 'Arial', sans-serif;">{gc_content:.1f}%</h3>
                            <p style="color: #444; font-size: 1.1em; font-family: 'Segoe UI', 'Arial', sans-serif;">GC Content</p>
                        </div>
                        <div class="stat-box" style="color: #222;">
                            <h3 style="color: #222; font-weight: 700; font-family: 'Segoe UI', 'Arial', sans-serif;">{topology.title()}</h3>
                            <p style="color: #444; font-size: 1.1em; font-family: 'Segoe UI', 'Arial', sans-serif;">Topology</p>
                        </div>
                        <div class="stat-box" style="color: #222;">
                            <h3 style="color: #222; font-weight: 700; font-family: 'Segoe UI', 'Arial', sans-serif;">{len(restriction_sites_list)}</h3>
                            <p style="color: #444; font-size: 1.1em; font-family: 'Segoe UI', 'Arial', sans-serif;">Restriction Sites</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Find restriction sites
                    normal_collection = find_restriction_sites(new_dna, restriction_sites_list, topology)
                    mutated_sites = build_mutated_restriction_sites(restriction_sites_list)
                    mutant_collection = find_restriction_sites(new_dna, mutated_sites, topology)
                    
                    # Display found sites
                    st.markdown("### 🎯 Found Restriction Sites")
                    if normal_collection.restriction_sites:
                        sites_data = []
                        for site in normal_collection.restriction_sites:
                            sites_data.append({
                                'Site': site.label,
                                'Position': site.position + 1,
                                'Pattern': site.iupac_pattern,
                                'Cut Distance': site.cut_distance
                            })
                        
                        df_sites = pd.DataFrame(sites_data)
                        st.dataframe(df_sites, use_container_width=True)
                    else:
                        st.info("No restriction sites found with current parameters.")
                    
                    # Display potential mutations
                    st.markdown("### 🧪 Potential Mutation Sites")
                    if mutant_collection.restriction_sites:
                        mut_data = []
                        for site in mutant_collection.restriction_sites:
                            mut_data.append({
                                'Mutation Site': site.label,
                                'Position': site.position + 1,
                                'Pattern': site.iupac_pattern,
                                'Cut Distance': site.cut_distance
                            })
                        
                        df_mutations = pd.DataFrame(mut_data)
                        st.dataframe(df_mutations, use_container_width=True)
                    else:
                        st.info("No potential mutation sites found.")
                    
                    # Sequence visualization
                    st.markdown("### 🧬 Sequence Visualization")
                    # Prepare a map of cut positions to enzyme names
                    cut_annotations = {}
                    for site in normal_collection.restriction_sites:
                        cut_pos = site.position
                        # Clamp cut_pos to valid range
                        if 0 <= cut_pos < len(new_dna):
                            # If multiple enzymes cut at same position, join names
                            if cut_pos not in cut_annotations:
                                cut_annotations[cut_pos] = []
                            cut_annotations[cut_pos].append(site.label.split(" at")[0])

                    nucleotide_colors = {
                        'A': '#1f77b4',  # Blue
                        'T': '#d62728',  # Red
                        'G': '#2ca02c',  # Green
                        'C': '#ff7f0e',  # Orange
                    }
                    formatted_sequence = ""
                    i = 0
                    while i < len(new_dna):
                        line_num = str(i + 1).rjust(8)
                        sequence_chunk = new_dna[i:i + bases_per_line]
                        colored_chunk = ""
                        j = 0
                        while j < len(sequence_chunk):
                            codon = sequence_chunk[j:j+3]
                            codon_colored = ""
                            for k, nt in enumerate(codon):
                                seq_pos = i + j + k
                                color = nucleotide_colors.get(nt.upper(), "#888")
                                # Check if this position is a cut site
                                if seq_pos in cut_annotations:
                                    # Add enzyme name above, only once per cut site
                                    enzyme_names = ", ".join(cut_annotations[seq_pos])
                                    codon_colored += (
                                        f"<div style='display:inline-block; text-align:center;'>"
                                        f"<span style='font-size:18px; background:#ffeaa7; color:#ed8936; font-weight:bold; border-radius:4px; padding:2px 6px; margin-bottom:2px;'>{enzyme_names}</span><br>"
                                        f"<span class='restriction-site' style='background:#fff3cd; color:#856404; font-weight:bold;'>{nt.upper()}</span>"
                                        f"</div>"
                                    )
                                else:
                                    codon_colored += f"<span style='color:{color}; font-weight:bold;'>{nt.upper()}</span>"
                            colored_chunk += codon_colored + " "
                            j += 3
                        formatted_sequence += f"{line_num} {colored_chunk.strip()}<br>"
                        i += bases_per_line

                    # For each selected reading frame, generate results
                    mutated_sites_info_all_frames = []
                    formatted_translation_all = {}
                    formatted_mut_translation_all = {}

                    for rf in reading_frame:
                        rf_offset = int(rf) - 1
                        dna_for_translation = new_dna[rf_offset:]
                        translation = translate_dna(dna_for_translation, genetic_code_dict)

                        # Format translation (no highlights in original)
                        formatted_translation = ""
                        amino_per_line = bases_per_line // 3
                        for i in range(0, len(translation), amino_per_line):
                            line_num = str(i + 1).rjust(8)
                            aa_chunk = translation[i:i + amino_per_line]
                            aa_display = " ".join(aa_chunk)
                            formatted_translation += f"{line_num} {aa_display}<br>"

                        formatted_translation_all[rf] = formatted_translation

                        # Translation (Mutated Sequence)
                        mutated_dna = list(new_dna)
                        aa_mut_cut_positions = set()
                        mutated_sites_info = []

                        # For each potential mutation site, check if it causes an amino acid change
                        for site in mutant_collection.restriction_sites:
                            pos = site.position
                            pattern = site.iupac_pattern.upper()
                            if 0 <= pos < len(mutated_dna) - len(pattern) + 1:
                                original_seq = ''.join(mutated_dna[pos:pos+len(pattern)])
                                mutated_seq = list(original_seq)
                                for i, base in enumerate(pattern):
                                    if base != 'N' and mutated_seq[i] != base:
                                        mutated_seq[i] = base
                                # Apply mutation temporarily
                                temp_dna = mutated_dna.copy()
                                temp_dna[pos:pos+len(pattern)] = mutated_seq
                                mutated_dna_str = ''.join(temp_dna)
                                mutated_translation = translate_dna(mutated_dna_str[rf_offset:], genetic_code_dict)
                                # Find which amino acids changed
                                for idx in range(min(len(translation), len(mutated_translation))):
                                    if translation[idx] != mutated_translation[idx]:
                                        codon_start = rf_offset + idx * 3
                                        codon_end = codon_start + 3
                                        if pos >= codon_start and pos < codon_end:
                                            aa_mut_cut_positions.add(idx)
                                            mutated_sites_info.append({
                                                "enzyme": site.label.split(" at")[0],
                                                "pos": pos+1,
                                                "original_seq": original_seq,
                                                "mutated_seq": ''.join(mutated_seq),
                                                "aa_idx": idx+1,
                                                "orig_aa": translation[idx],
                                                "mut_aa": mutated_translation[idx],
                                                "reading_frame": rf
                                            })
                                            break
                        # Apply all mutations for display
                        for info in mutated_sites_info:
                            pos = info["pos"] - 1
                            pattern = info["mutated_seq"]
                            mutated_dna[pos:pos+len(pattern)] = list(pattern)
                        mutated_translation = translate_dna(''.join(mutated_dna)[rf_offset:], genetic_code_dict)

                        # Format mutated translation with highlights at all changed amino acids
                        formatted_mut_translation = ""
                        for i in range(0, len(mutated_translation), amino_per_line):
                            line_num = str(i + 1).rjust(8)
                            aa_chunk = mutated_translation[i:i + amino_per_line]
                            aa_display = ""
                            for j, aa in enumerate(aa_chunk):
                                idx = i + j
                                if idx in aa_mut_cut_positions:
                                    aa_display += f"<span class='mutation-highlight' style='background:#f8d7da; color:#721c24; font-weight:bold;'>{aa}</span> "
                                else:
                                    aa_display += f"{aa} "
                            formatted_mut_translation += f"{line_num} {aa_display.strip()}<br>"

                        formatted_mut_translation_all[rf] = formatted_mut_translation
                        mutated_sites_info_all_frames.extend(mutated_sites_info)

                        # Show results for this reading frame
                        # First show DNA sequence, then amino acid sequence below
                        st.markdown(f"""
                        <div class="result-box">
                            <h4>📝 {title} (Reading Frame {rf})</h4>
                            <div class="dna-sequence" style="background:#f8f9fa; border:1px solid #dee2e6; border-radius:5px; padding:1rem; font-size:20px; max-height:350px; overflow-y:auto; overflow-x:hidden; white-space:pre-line;">
                                {formatted_sequence}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="result-box">
                            <h4>🧬 Amino Acid Sequence (Original, Reading Frame {rf})</h4>
                            <div class="dna-sequence" style="background:#f8f9fa; border:1px solid #dee2e6; border-radius:5px; padding:1rem; font-size:22px; max-height:350px; overflow-y:auto; overflow-x:hidden; white-space:pre-line;">
                                {formatted_translation}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="result-box">
                            <h4>🧬 Amino Acid Sequence (With Mutation, Reading Frame {rf})</h4>
                            <div class="dna-sequence" style="background:#f8f9fa; border:1px solid #dee2e6; border-radius:5px; padding:1rem; font-size:22px; max-height:350px; overflow-y:auto; overflow-x:hidden; white-space:pre-line;">
                                {formatted_mut_translation}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # DNA sequence visualization (shown only once if multiple frames)
                    # (Already shown above for each frame, so skip here)

                    # Mutation information (show ALL possible mutations, for ALL reading frames, with clear indication of protein-changing vs silent)
                    if mutant_collection.restriction_sites:
                        bg_gradients = [
                            "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                            "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
                            "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                            "linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%)",
                            "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
                            "linear-gradient(135deg, #f8d7da 0%, #f093fb 100%)",
                        ]
                        # CSS for animation and highlights
                        st.markdown("""
                        <style>
                        @keyframes fadeInMove {
                            0% { opacity: 0; transform: translateY(30px) scale(0.98); }
                            100% { opacity: 1; transform: translateY(0) scale(1); }
                        }
                        .mutation-anim-block {
                            animation: fadeInMove 0.9s cubic-bezier(.4,0,.2,1);
                        }
                        .mutation-aa-change {
                            background: #f8d7da;
                            color: #721c24;
                            border-radius: 4px;
                            padding: 0.2em 0.5em;
                            font-weight: bold;
                            border: 1px solid #f5c6cb;
                            font-family: 'Courier New', monospace;
                            font-size: 1.1em;
                            transition: background 0.4s;
                        }
                        .mutation-arrow {
                            font-size: 1.7em;
                            margin: 0 0.5em;
                            vertical-align: middle;
                            animation: fadeInMove 1.2s cubic-bezier(.4,0,.2,1);
                        }
                        .mutation-silent {
                            color: #008000 !important;
                            font-size: 1.1em;
                            margin-left: 0.5em;
                            font-weight: bold;
                            background: #e6ffe6;
                            padding: 0.15em 0.6em;
                            border-radius: 4px;
                            border: 1px solid #b2ffb2;
                            box-shadow: 0 1px 4px rgba(0,128,0,0.07);
                            display: inline-block;
                        }
                        .mutation-nonsilent {
                            color: #b30000 !important;
                            font-size: 1.1em;
                            margin-left: 0.5em;
                            font-weight: bold;
                            background: #ffd6d6;
                            padding: 0.15em 0.6em;
                            border-radius: 4px;
                            border: 1px solid #ffb2b2;
                            box-shadow: 0 1px 4px rgba(179,0,0,0.07);
                            display: inline-block;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        # For each mutation site, for each reading frame, show info
                        enzyme_blocks = []
                        for idx, site in enumerate(mutant_collection.restriction_sites):
                            pos = site.position
                            pattern = site.iupac_pattern.upper()
                            # Try to extract enzyme name from label or fallback
                            enzyme = site.label.split(" at")[0]
                            # Clean enzyme name for display (remove extra chars if any)
                            enzyme_display = enzyme
                            # Try to get enzyme name from pattern if label is not clean
                            if enzyme_display.startswith("(") and enzyme_display.endswith(")"):
                                enzyme_display = enzyme_display[1:-1]
                            # If enzyme name is empty, fallback to pattern
                            if not enzyme_display.strip():
                                enzyme_display = pattern
                            # Use first two uppercase letters for icon, or fallback to 'E'
                            enzyme_icon = ''.join([c for c in enzyme_display if c.isalnum()])[:2].upper() or "E"

                            original_seq = new_dna[pos:pos+len(pattern)] if 0 <= pos < len(new_dna) - len(pattern) + 1 else ""
                            mutated_seq = ""
                            # Build mutated sequence (replace non-N with pattern base)
                            if original_seq:
                                mutated_seq_list = list(original_seq)
                                for i, base in enumerate(pattern):
                                    if base != 'N' and mutated_seq_list[i] != base:
                                        mutated_seq_list[i] = base
                                mutated_seq = ''.join(mutated_seq_list)
                            # For each reading frame, check effect
                            for rf in reading_frame:
                                rf_offset = int(rf) - 1
                                # Only consider if mutation overlaps a codon in this frame
                                codon_start = ((pos - rf_offset) // 3) * 3 + rf_offset
                                codon_end = codon_start + 3
                                if codon_start < 0 or codon_end > len(new_dna):
                                    continue
                                # Apply mutation to a copy
                                temp_dna = list(new_dna)
                                if original_seq and mutated_seq:
                                    temp_dna[pos:pos+len(pattern)] = list(mutated_seq)
                                mutated_dna_str = ''.join(temp_dna)
                                translation = translate_dna(new_dna[rf_offset:], genetic_code_dict)
                                mutated_translation = translate_dna(mutated_dna_str[rf_offset:], genetic_code_dict)
                                aa_idx = ((pos - rf_offset) // 3) + 1
                                # Find which amino acid(s) in this codon changed
                                orig_aa = translation[aa_idx-1] if aa_idx-1 < len(translation) else "-"
                                mut_aa = mutated_translation[aa_idx-1] if aa_idx-1 < len(mutated_translation) else "-"
                                is_silent = orig_aa == mut_aa
                                # Only show if original_seq and mutated_seq are valid
                                if not original_seq or not mutated_seq:
                                    continue
                                block = f"""
                                <div class="mutation-anim-block" style="background: {bg_gradients[idx % len(bg_gradients)]}; border-radius: 12px; margin-bottom: 1.2rem; padding: 1.2rem 1.2rem 1.2rem 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.07); transition: box-shadow 0.3s;">
                                    <div style="display: flex; align-items: center; gap: 1.2rem;">
                                        <div style="flex-shrink:0;">
                                            <span style="display:inline-block; background:#fff3cd; color:#856404; font-weight:700; border-radius:50%; width:48px; height:48px; text-align:center; line-height:48px; font-size:1.7em; border:2px solid #ed8936; box-shadow:0 2px 8px #ffeaa7;">
                                                {enzyme_icon}
                                            </span>
                                        </div>
                                        <div style="flex-grow:1;">
                                            <h4 style="margin:0 0 0.3em 0; color:#222;">{enzyme_display}</h4>
                                            <div style="font-size:1.1em; margin-bottom:0.5em;">
                                                <b>Restriction site can be introduced at:</b> <span style="color:#721c24;">Position {pos+1}</span> (Reading Frame {rf})
                                            </div>
                                            <div style="display:flex; align-items:center; gap:0.7em; margin-bottom:0.4em;">
                                                <span style="font-family:'Courier New',monospace; background:#f8f9fa; border-radius:4px; padding:0.2em 0.5em; border:1px solid #dee2e6;">
                                                    {original_seq}
                                                </span>
                                                <span class="mutation-arrow">→</span>
                                                <span style="font-family:'Courier New',monospace; background:#ffeaa7; border-radius:4px; padding:0.2em 0.5em; border:1px solid #ed8936;">
                                                    {mutated_seq}
                                                </span>
                                            </div>
                                            <div style="margin-top:0.5em; font-size:1.08em;">
                                                <b>Amino acid change:</b>
                                                <span class="mutation-aa-change">{orig_aa}{aa_idx}{mut_aa}</span>
                                                {f"<span class='mutation-silent'>&#10004; Silent</span>" if is_silent else "<span class='mutation-nonsilent'>&#9888; Protein-Might-change</span>"}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """
                                enzyme_blocks.append(block)
                        # Only render as HTML if there is at least one valid block
                        if enzyme_blocks:
                            st.markdown(
                                f"""
                                <div class="info-box" style="max-height: 500px; overflow-y: auto; padding-right: 1em;">
                                    <h4 style="margin-bottom:1em;">🔄 Mutation Information (All Reading Frames)</h4>
                                    {''.join(enzyme_blocks)}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.info("No valid mutation information available.")
                    else:
                        st.info("No potential mutation sites found for any reading frame.")

                    # For download, generate results for all selected reading frames
                    st.markdown("### 💾 Download Results")

                    # --- Dynamic summary for the report ---
                    summary_lines = []
                    summary_lines.append(f"The sequence analyzed is <b>{title}</b> with length <b>{len(new_dna)} bp</b> and GC content <b>{gc_content:.1f}%</b>.")
                    if normal_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(normal_collection.restriction_sites)}</b> restriction site(s) were found in the sequence for the selected enzymes.")
                    else:
                        summary_lines.append("No restriction sites were found for the selected enzymes in the sequence.")
                    if mutant_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(mutant_collection.restriction_sites)}</b> potential mutation site(s) were identified where a single or double base change could introduce a new restriction site.")
                    else:
                        summary_lines.append("No potential mutation sites were found where a new restriction site could be introduced by a small change.")
                    # Count protein-changing mutations across all frames
                    total_mutated_sites_info = [info for info in mutated_sites_info_all_frames]
                    if total_mutated_sites_info:
                        summary_lines.append(f"<b>{len(total_mutated_sites_info)}</b> mutation(s) would also change the protein sequence at the restriction site position (highlighted in the report).")
                    else:
                        summary_lines.append("None of the potential mutation sites would change the protein sequence at the restriction site position.")
                    summary_lines.append("This report provides a summary of restriction sites, possible new sites by mutation, and the effect of these changes on the protein translation. Use this to plan cloning or mutagenesis experiments and to check if introducing a restriction site will also alter the protein.")

                    html_summary = "<ul style='font-size:1.1em;'>" + "".join([f"<li>{line}</li>" for line in summary_lines]) + "</ul>"

                    # Prepare HTML sections for each reading frame
                    html_rf_sections = ""
                    plain_rf_sections = ""
                    for rf in reading_frame:
                        rf_title = f"Reading Frame {rf}"
                        formatted_translation = formatted_translation_all[rf]
                        formatted_mut_translation = formatted_mut_translation_all[rf]
                        mutated_sites_info = [info for info in mutated_sites_info_all_frames if info["reading_frame"] == rf]
                        html_rf_sections += f"""
                        <div class="section">
                            <h2>🔬 Protein Translation (Original, {rf_title})</h2>
                            <div class="aa-sequence">{formatted_translation}</div>
                        </div>
                        <div class="section">
                            <h2>🧬 Protein Translation (With Mutation, {rf_title})</h2>
                            <div class="aa-sequence">{formatted_mut_translation}</div>
                        </div>
                        <div class="section">
                            <h2>🔄 Mutation Information ({rf_title})</h2>
                            {"".join([
                                f"<div class='enzyme-block'><b>{info['enzyme']}</b> can be introduced at <b>position {info['pos']}</b> by changing <span class='dna-sequence' style='display:inline;background:#f8f9fa;'>{info['original_seq']}</span> → <span class='dna-sequence' style='display:inline;background:#ffeaa7;'>{info['mutated_seq']}</span>. This causes an amino acid change at position <span class='mutation-highlight'>{info['aa_idx']}</span>: <span class='mutation-highlight'>{info['orig_aa']}→{info['mut_aa']}</span>.</div>"
                                for info in mutated_sites_info
                            ]) if mutated_sites_info else "<i>No potential mutation sites found that would change the amino acid at a restriction site position in this reading frame.</i>"}
                        </div>
                        """
                        # Plain text for this reading frame
                        plain_rf_sections += f"\n=== PROTEIN TRANSLATION (Original, {rf_title}) ===\n"
                        plain_rf_sections += _re.sub('<[^<]+?>', '', formatted_translation.replace('<br>', '\n')) + "\n"
                        plain_rf_sections += f"\n=== PROTEIN TRANSLATION (With Mutation, {rf_title}) ===\n"
                        plain_rf_sections += _re.sub('<[^<]+?>', '', formatted_mut_translation.replace('<br>', '\n')) + "\n"
                        plain_rf_sections += f"\n=== MUTATION INFORMATION ({rf_title}) ===\n"
                        if mutated_sites_info:
                            for mutated_site_info in mutated_sites_info:
                                plain_rf_sections += (
                                    f"Restriction enzyme {mutated_site_info['enzyme']} can be introduced at position {mutated_site_info['pos']} "
                                    f"by changing {mutated_site_info['original_seq']} to {mutated_site_info['mutated_seq']}. "
                                    f"This causes an amino acid change at position {mutated_site_info['aa_idx']} from "
                                    f"{mutated_site_info['orig_aa']} to {mutated_site_info['mut_aa']}.\n"
                                )
                            plain_rf_sections += (
                                "\nThe highlighted amino acids in the mutated translation indicate where new restriction sites could be introduced "
                                "by nucleotide changes that also alter the amino acid. Refer to the 'Found Restriction Sites' section above for the exact enzyme and position.\n"
                            )
                        else:
                            plain_rf_sections += "No potential mutation sites found that would change the amino acid at a restriction site position in this reading frame.\n"

                    # Prepare a visually enhanced HTML report for download
                    # --- Enhanced dynamic summary for the report ---
                    summary_lines = []
                    summary_lines.append(f"The sequence analyzed is <b>{title}</b> with length <b>{len(new_dna)} bp</b> and GC content <b>{gc_content:.1f}%</b>.")
                    summary_lines.append(f"<b>DNA topology:</b> {topology.title()}.")
                    summary_lines.append(f"<b>Restriction enzymes analyzed:</b> {', '.join([site.split('(')[1].split(')')[0] for site in restriction_sites_list])}.")
                    summary_lines.append(f"<b>Reading frame(s) selected:</b> {', '.join(reading_frame)}.")
                    if normal_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(normal_collection.restriction_sites)}</b> restriction site(s) were found in the sequence for the selected enzymes.")
                    else:
                        summary_lines.append("No restriction sites were found for the selected enzymes in the sequence.")
                    if mutant_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(mutant_collection.restriction_sites)}</b> potential mutation site(s) were identified where a single or double base change could introduce a new restriction site.")
                    else:
                        summary_lines.append("No potential mutation sites were found where a new restriction site could be introduced by a small change.")
                    # Count protein-changing mutations across all frames
                    total_mutated_sites_info = [info for info in mutated_sites_info_all_frames]
                    if total_mutated_sites_info:
                        summary_lines.append(f"<b>{len(total_mutated_sites_info)}</b> mutation(s) would also change the protein sequence at the restriction site position (highlighted in the report).")
                    else:
                        summary_lines.append("None of the potential mutation sites would change the protein sequence at the restriction site position.")
                    # Add more details about reading frames and translation
                    summary_lines.append(f"Protein translation was performed for reading frame(s): <b>{', '.join(reading_frame)}</b>.")
                    for rf in reading_frame:
                        rf_mut = [info for info in mutated_sites_info_all_frames if info["reading_frame"] == rf]
                        summary_lines.append(
                            f"In reading frame <b>{rf}</b>: "
                            f"{'No protein-changing mutations detected.' if not rf_mut else f'<b>{len(rf_mut)}</b> mutation(s) would alter the amino acid sequence.'}"
                        )
                    summary_lines.append("This report provides a summary of restriction sites, possible new sites by mutation, and the effect of these changes on the protein translation. Use this to plan cloning or mutagenesis experiments and to check if introducing a restriction site will also alter the protein.")

                    html_summary = "<ul style='font-size:1.1em;'>" + "".join([f"<li>{line}</li>" for line in summary_lines]) + "</ul>"

                    # Prepare a visually enhanced HTML report for download
                    html_report = f"""
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <title>Mutate for Digest Analysis Results</title>
                        <style>
                            body {{
                                font-family: 'Segoe UI', Arial, sans-serif;
                                background: #f8f9fa;
                                color: #222;
                                margin: 0;
                                padding: 0 0 2em 0;
                            }}
                            .header {{
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: #fff;
                                padding: 2em 1em 1em 1em;
                                border-radius: 0 0 16px 16px;
                                text-align: center;
                            }}
                            .section {{
                                background: #fff;
                                border-radius: 10px;
                                margin: 2em auto 1.5em auto;
                                max-width: 900px;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.07);
                                padding: 2em 2em 1.5em 2em;
                            }}
                            .stat-box {{
                                display: inline-block;
                                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                                padding: 1em 2em;
                                border-radius: 10px;
                                margin: 0 1em 1em 0;
                                text-align: center;
                                min-width: 120px;
                                font-size: 1.1em;
                                font-weight: 600;
                                color: #222;
                            }}
                            .dna-sequence, .aa-sequence {{
                                font-family: 'Courier New', monospace;
                                font-size: 1.1em;
                                background: #f8f9fa;
                                border-radius: 5px;
                                border: 1px solid #dee2e6;
                                padding: 1em;
                                margin: 1em 0;
                                overflow-x: auto;
                                white-space: pre-line;
                            }}
                            .restriction-site {{
                                background: #fff3cd;
                                color: #856404;
                                font-weight: bold;
                                border-radius: 3px;
                                padding: 0.1em 0.3em;
                            }}
                            .mutation-highlight {{
                                background: #f8d7da;
                                color: #721c24;
                                font-weight: bold;
                                border-radius: 3px;
                                padding: 0.1em 0.3em;
                            }}
                            .enzyme-block {{
                                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                border-radius: 10px;
                                margin-bottom: 1.2em;
                                padding: 1.2em;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.07);
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>🧬 Mutate for Digest Analysis Results</h1>
                            <div>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                        </div>
                        <div class="section">
                            <h2>ℹ️ Report Summary</h2>
                            {html_summary}
                        </div>
                        <div class="section">
                            <h2>📄 Sequence Summary</h2>
                            <div class="stat-box">Length<br>{len(new_dna)} bp</div>
                            <div class="stat-box">GC Content<br>{gc_content:.1f}%</div>
                            <div class="stat-box">Topology<br>{topology.title()}</div>
                            <div class="stat-box">Restriction Sites<br>{len(restriction_sites_list)}</div>
                            <div style="margin-top:1em;"><b>Sequence:</b> {title}</div>
                            <div><b>Restriction Sites Analyzed:</b> {', '.join([site.split('(')[1].split(')')[0] for site in restriction_sites_list])}</div>
                            <div><b>Reading Frame(s):</b> {', '.join(reading_frame)}</div>
                        </div>
                        <div class="section">
                            <h2>🎯 Found Restriction Sites</h2>
                            {"<ul>" + "".join([f"<li><span class='restriction-site'>{site.label}</span> - Pattern: <b>{site.iupac_pattern}</b> - Cut Distance: {site.cut_distance}</li>" for site in normal_collection.restriction_sites]) + "</ul>" if normal_collection.restriction_sites else "<i>No restriction sites found with current parameters.</i>"}
                        </div>
                        <div class="section">
                            <h2>🧪 Potential Mutation Sites</h2>
                            {"<ul>" + "".join([f"<li><span class='mutation-highlight'>{site.label}</span> - Pattern: <b>{site.iupac_pattern}</b> - Cut Distance: {site.cut_distance}</li>" for site in mutant_collection.restriction_sites]) + "</ul>" if mutant_collection.restriction_sites else "<i>No potential mutation sites found.</i>"}
                        </div>
                        <div class="section">
                            <h2>🧬 Sequence Visualization</h2>
                            <div class="dna-sequence">{formatted_sequence}</div>
                        </div>
                        {html_rf_sections}
                    </body>
                    </html>
                    """

                    # Also provide a plain text version for compatibility
                    plain_text = f"""Mutate for Digest Analysis Results
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
{"".join([_re.sub('<[^<]+?>', '', line) for line in summary_lines])}

Sequence: {title}
Length: {len(new_dna)} bp
GC Content: {gc_content:.1f}%
Topology: {topology}
Restriction Sites Analyzed: {', '.join([site.split('(')[1].split(')')[0] for site in restriction_sites_list])}

=== RESTRICTION SITES FOUND ===
"""
                    if normal_collection.restriction_sites:
                        for site in normal_collection.restriction_sites:
                            plain_text += f"{site.label} - Pattern: {site.iupac_pattern} - Cut Distance: {site.cut_distance}\n"
                    else:
                        plain_text += "No restriction sites found with current parameters.\n"

                    plain_text += "\n=== POTENTIAL MUTATION SITES ===\n"
                    if mutant_collection.restriction_sites:
                        for site in mutant_collection.restriction_sites:
                            plain_text += f"{site.label} - Pattern: {site.iupac_pattern} - Cut Distance: {site.cut_distance}\n"
                    else:
                        plain_text += "No potential mutation sites found.\n"

                    plain_text += "\n=== DNA SEQUENCE (with cut site annotations) ===\n"
                    plain_seq = _re.sub('<[^<]+?>', '', formatted_sequence.replace('<br>', '\n'))
                    plain_text += plain_seq + "\n"

                    plain_text += plain_rf_sections

                    # Download buttons for both HTML (visual) and plain text
                    st.download_button(
                        label="📄 Download Visual HTML Report",
                        data=html_report,
                        file_name=f"mutate_digest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                    st.download_button(
                        label="📄 Download Plain Text Results",
                        data=plain_text,
                        file_name=f"mutate_digest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

if __name__ == "__main__":
    main()