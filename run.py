mport sys
import os
import time
from itertools import zip_longest, product
from datetime import datetime


def read_fasta(file_path):
    """Reads a FASTA file and returns sequences with headers."""
    sequences = []
    current_seq = []
    header = None
   
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(">"):  # FASTA header
                if header and current_seq:
                    sequences.append((header, "".join(current_seq)))
                header = line  # Store new header
                current_seq = []
            else:
                current_seq.append(line)

        if header and current_seq:
            sequences.append((header, "".join(current_seq)))  # Add last sequence

    return sequences

def html_starter(header):
    return f"""
    <html>
        <head>
            <script src='https://code.jquery.com/jquery-3.6.0.min.js'></script>

            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }}
                pre {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-size: 16px;
                    width: 100%;
                    overflow-wrap: break-word;
                }}
                .primer {{
                    font-weight: bold;
                    font-size: 16px;
                }}
                #primer-navigation {{
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    width: 570px;
                    background: rgba(255, 255, 255, 0.96);
                    padding: 10px;
                    border-radius: 18px;
                    box-shadow: 0px 0px 4px lightblue;
                    z-index: 1;
                    font-size: 14px;
                }}

                .styled-button {{
                    cursor: pointer;
                    display: inline-block;
                    padding: 0 5px;
                    font-size: 16px;
                    text-decoration: none;
                    width: 25px;
                    box-shadow: 1px 1px 1px rgba(0, 140, 255);
                    text-align: center;
                    border-radius: 8px;  
                    color: white;
                    transition: all 0.3s ease;
                }}
            .counter {{
                color: dodgerblue;
            }}

            .styled-button:hover {{
                background-color: #0099cc;
                box-shadow: 1px 1px 6px rgba(0, 140, 255);
            }}

            .styled-button:active {{
                box-shadow: none;
            }}


            .buttons {{
                margin-right: 12px;
                user-select: none;
                -webkit-user-select: none; /* For Safari */
                -moz-user-select: none; /* For Firefox */
                -ms-user-select: none; /* For Internet Explorer/Edge */
            }}
        </style>
        </head>
        <body>
            <br>
            <pre><strong>{header}</strong>\n
        """

def calcul_primers_distances(data):
    """
    Compares 'dist' values one by one and adds 'len' to the greater number.
    The dist contains the location of the primer start location
    We don't know if we have the pr1 first, or the pr2
    So when a primer location is greater, it's mean the primer come after
    For example, pr1 = 50 and pr2 = 100, so whe need to add pr2 lenght to get
    the all sequence length
    """
    result = []
    dist1, len1 = data['pr1']['dist'], data['pr1']['len']
    dist2, len2 = data['pr2']['dist'], data['pr2']['len']
    for d1, d2 in zip(dist1, dist2):
        # print(d1, d2, len1, len2)
        if d1 > d2:
            result.append(d1 + len1 - d2)
        else:
            result.append(d2 + len2 - d1)

    return result

def find_contig_primers(idx, header, sequence, primers, colors):
    """Highlight primer sequences in an HTML format with proper styling."""
   
    global ANCHORS_COUNT_PR1
    global ANCHORS_COUNT_PR2
    global ANCHORS_COUNT_PROBE
    global PR1_ANCHOR_PREFIX
    global PR2_ANCHOR_PREFIX
    global PR3_ANCHOR_PREFIX

    html_content = html_starter(header)
    sequence_upper = sequence.upper()
    primers_upper = [p.upper() for p in primers]
    distances = []
    color_count = len(colors)
    contigs = { idx: {}}
    i = 0

    # Will iterate through the contig
    # j : 0 for primer 1, 1 for primer 2, 2 for primer 3
    # Add anchor in each probe to be easily fetched by the search window
    count = 0
    while i < len(sequence):
        matched = False

        for j, primer in enumerate(primers_upper):
            if sequence_upper[i:i + len(primer)] == primer:              
                count += 1
                if j == 0:
                    if 'pr1' not in contigs[idx]:
                        contigs[idx]['pr1'] = {'dist': [], 'len': len(primer)}
                    contigs[idx]['pr1']['dist'].append(i)
                elif j == 1:                    
                    if 'pr2' not in contigs[idx]:
                        contigs[idx]['pr2'] = {'dist': [], 'len': len(primer)}
                    contigs[idx]['pr2']['dist'].append(i)
                color = colors[j % color_count]
   
                if j == 0:
                    ANCHORS_COUNT_PR1 += 1
                    custom_id = f"{PR1_ANCHOR_PREFIX}{ANCHORS_COUNT_PR1}"
                elif j == 1:
                    ANCHORS_COUNT_PR2 += 1
                    custom_id = f"{PR2_ANCHOR_PREFIX}{ANCHORS_COUNT_PR2}"
                else:
                    ANCHORS_COUNT_PROBE +=1
                    custom_id = f"{PR3_ANCHOR_PREFIX}{ANCHORS_COUNT_PROBE}"

                html_content += f"<span id={custom_id} class='primer' style='background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});font-size:16px'>{sequence[i:i + len(primer)]}</span>"
                i += len(primer)
                matched = True
                break

        if not matched:
            html_content += sequence[i]
            i += 1

    # Calcul sequence length beween pr1 et pr2
    # With the 'contigs' we have position/appareance of each primer (0, 1, 2 ..)
    contig = contigs[idx]
    if len(contig) > 0 and 'pr1' in contig and 'pr2' in contig:
        distances = calcul_primers_distances(contig)
    html_content += "</pre></body></html>"
   
    return html_content, distances

def save_html(html_content, output_dir, input_filename):
    """Save the highlighted sequence to an HTML file in the 'results/' directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = os.path.splitext(os.path.basename(input_filename))[0] + "_highlighted.html"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w") as file:
        file.write(html_content)
   
    return output_path

def log_message(log_dir, message):
    """Save log messages with timestamps."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_file = os.path.join(log_dir, f"log_{timestamp}.txt")

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

    return log_file

def create_navigation_window(distances, anchors_count):
    pr1_max, pr2_max, pr3_max = anchors_count
    nav = '<div id="primer-navigation">'
    header = ''
    content = ''
    logic = f"""
            <script>
            $(document).ready(function() {{
                pr1_count = 0;
                pr2_count = 0;
                pr3_count = 0;

                setWindowHash = (hash) => {{
                    window.location.hash = hash
                }}

                $('#primer1_up').on('click', function() {{
                    if (pr1_count == {pr1_max}) {{
                        pr1_count = 1;
                        setWindowHash('');
                    }}
                    else
                        pr1_count++;
                    const target_id = 'pr1_' + pr1_count;
                    $(".count_1").text(pr1_count);
                    setWindowHash(target_id);
                }});
                $('#primer1_down').on('click', function() {{
                    if (pr1_count > 1) {{
                        pr1_count --;
                        setWindowHash('')
                    }}
                    else
                        setWindowHash('')
                    const target_id = 'pr1_' + pr1_count;
                    $(".count_1").text(pr1_count);
                    setWindowHash(target_id);
                }});

                $('#primer2_up').on('click', function() {{
                    if (pr2_count == {pr2_max}) {{
                        pr2_count = 1;
                        setWindowHash('')
                    }}
                    else
                        pr2_count++;
                    const target_id = 'pr2_' + pr2_count;
                    $(".count_2").text(pr2_count);
                    setWindowHash(target_id);
                }});
                $('#primer2_down').on('click', function() {{
                    if (pr2_count > 1) {{
                        pr2_count --;
                        setWindowHash('')
                    }}
                    const target_id = 'pr2_' + pr2_count;
                    $(".count_2").text(pr2_count);
                    setWindowHash(target_id);
                }});

                $('#primer3_up').on('click', function() {{
                    if (pr3_count == {pr3_max}) {{
                        pr3_count = 1;
                        setWindowHash('')
                    }}
                    else
                        pr3_count ++;

                    const target_id = 'pr3_' + pr3_count;
                    $(".count_3").text(pr3_count);
                    setWindowHash(target_id);
                }});
                $('#primer3_down').on('click', function() {{
                    if (pr3_count > 1) {{
                        pr3_count --;
                        setWindowHash('')
                    }}
                    const target_id = 'pr3_' + pr3_count;
                    $(".count_3").text(pr3_count);
                    setWindowHash(target_id);
                }});
            }})
            </script>
        """
   
    if distances:
        header += f'&#129516; <b>Found:</b> {len(distances)} sequence(s) <br>'
        header += '&#128295; <b>Length:</b>'
       
        for i, d in enumerate(distances):
            content += f"<span> {d} bp</span>"
            if i < len(distances)-1:
                content += ','
        content += '<br><br>'
        content += logic
    elif pr1_max or pr2_max or pr3_max:
        header += '&#129516; <b>Found:</b><br><br>'
        content += logic  
    else:
        header += '&#129516; <b>No data founded !</b><br>'
   
    if pr1_max:
        content += f'''
            <div><span class="buttons">
            Primer 1
            <a id="primer1_up" style="background-color: #FFAC1C;" class="styled-button" >&#11014</a>
            <a id="primer1_down" style="background-color: #FFD580" class="styled-button" >&#11015</a>
            <span class="counter"><span class="count_1">0</span>/{pr1_max}</span>
            </span>
        '''
    if pr2_max:
        content += f'''
            <span class="buttons">
                Primer 2
                <a id="primer2_up"  style="background-color: #FF0000;" class="styled-button" >&#11014</a>
                <a id="primer2_down"  style="background-color: #E97451;" class="styled-button" >&#11015</a>
                <span class="counter"><span class="count_2">0</span>/{pr2_max}</span>
            </span>
        '''
    if pr3_max:
        content += f'''
            <span class="buttons">
                Probe
                <a id="primer3_up" style="background-color: #FF3659;" class="styled-button" >&#11014</a>
                <a id="primer3_down" style="background-color: #FF647F;" class="styled-button" >&#11015</a>
                <span class="counter"><span class="count_3">0</span>/{pr3_max}</span>
            </span>
        </div>
        '''

   
    return f"""
            {nav}
            {header}
            {content}
        </div>  
        """
   
def invert_complement_dna(sequence: str):
    """
    Inverts (reverses) and complements a DNA sequence.
    Example: ATCG -> CGAT
    """
    complement = {
        'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'
    }
    sequence = sequence.upper()
    return ''.join(complement[base] for base in reversed(sequence))

def generate_combinations(sequences):
    """
    Generates all possible combinations of the given sequences
    in both forward and inverted-complement forms.
    """
    all_variants = [(seq, invert_complement_dna(seq)) for seq in sequences]
    return [list(combo) for combo in product(*all_variants)]


ANCHORS_COUNT_PR1 = 0
ANCHORS_COUNT_PR2 = 0
ANCHORS_COUNT_PROBE = 0
PR1_ANCHOR_PREFIX = 'pr1_'
PR2_ANCHOR_PREFIX = 'pr2_'
PR3_ANCHOR_PREFIX = 'pr3_'

start_time = time.time()
print("[>>>] Processing...")

if len(sys.argv) != 6:
    print("[X] Usage: python run.py input.fasta primer1 primer2 probe workingDir")
    sys.exit(1)

fasta_file = sys.argv[1]
primers = [sys.argv[2], sys.argv[3], sys.argv[4]]
output_dir = f"{sys.argv[5]}/results"
log_dir = "logs"

# Get all combination from the primers forward - reverse
all_primers_combinations = generate_combinations(primers)

primers_colors = [
    (1, 0.7, 0),    
    (1, 0, 0),  
    (1, 0.75, 0.8)  
]

log_file = log_message(log_dir, f"Starting processing for {fasta_file}")

if not os.path.exists(fasta_file):
    error_msg = f"[X] Error: File '{fasta_file}' not found."
    print(error_msg)
    log_message(log_dir, error_msg)
    sys.exit(1)

sequences = read_fasta(fasta_file)
if not sequences:
    error_msg = "[X] No DNA sequences found in the FASTA file."
    print(error_msg)
    log_message(log_dir, error_msg)
    sys.exit(1)

html_outputs = []
seq_distances = []

# Enumerate each contigs
# When finded pr1 et 2, calcul the distance to display it in the window
matches_counter = 0
matched = {}

'''
We want to check all combination forw and reverse for all primers/probe
to be sur not miss some sequence
'''
print("[Lazy Moti Mode]  Fetch all primers combinations (forw, rev) automatically")

for primers_combination in all_primers_combinations:
    html_outputs = []
    for idx, (header, seq) in enumerate(sequences):
        html_output, distances = find_contig_primers(idx, header, seq, primers_combination, primers_colors)

        if distances:
            seq_distances.extend(distances)

        html_outputs.append(html_output)

    new_matches_counter = ANCHORS_COUNT_PR1 + ANCHORS_COUNT_PR2 + ANCHORS_COUNT_PROBE
   
    if new_matches_counter > matches_counter:
        matches_counter = new_matches_counter
        matched = {
            'matches_counter': matches_counter,
            'pr1_count': ANCHORS_COUNT_PR1,
            'pr2_count': ANCHORS_COUNT_PR2,
            'pr3_count': ANCHORS_COUNT_PROBE,
            'html_outputs': html_outputs
        }

    ANCHORS_COUNT_PR1 = 0
    ANCHORS_COUNT_PR2 = 0
    ANCHORS_COUNT_PROBE = 0

if matched:
    matched['html_outputs'].append(
        create_navigation_window(
            distances=seq_distances,
            anchors_count=[
                matched['pr1_count'],
                matched['pr2_count'],
                matched['pr3_count']]
            )
        )
    output_path = save_html("\n".join(matched['html_outputs']), output_dir, fasta_file)

    elapsed_time = int(time.time() - start_time)
    success_msg = f"[OK] Processing completed in {elapsed_time} seconds. Output saved to {output_path}"

    print(success_msg)
    log_message(log_dir, success_msg)
