from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

# Helper to draw a block arrow using path
def draw_block_arrow(c, x, y, width, height, direction="right", color=colors.black, fill_color=colors.white):
    c.setStrokeColor(color)
    c.setFillColor(fill_color)
    c.setLineWidth(1.5)
    p = c.beginPath()
    
    if direction == "right":
        head_l = width * 0.4
        tail_h = height * 0.5
        y_center = y
        p.moveTo(x, y_center + tail_h/2)
        p.lineTo(x + width - head_l, y_center + tail_h/2)
        p.lineTo(x + width - head_l, y_center + height/2)
        p.lineTo(x + width, y_center)
        p.lineTo(x + width - head_l, y_center - height/2)
        p.lineTo(x + width - head_l, y_center - tail_h/2)
        p.lineTo(x, y_center - tail_h/2)
        p.close()
    c.drawPath(p, fill=1, stroke=1)

def draw_custom_arrow(c, points, color=colors.black, fill_color=colors.white):
    c.setStrokeColor(color)
    c.setFillColor(fill_color)
    c.setLineWidth(1.5)
    p = c.beginPath()
    p.moveTo(points[0][0], points[0][1])
    for x, y in points[1:]:
        p.lineTo(x, y)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

def draw_double_arrow(c, x, y, width, height, color=colors.black, fill_color=colors.white):
    c.setStrokeColor(color)
    c.setFillColor(fill_color)
    c.setLineWidth(1.5)
    p = c.beginPath()
    head_l = width * 0.3
    tail_h = height * 0.4
    
    p.moveTo(x + head_l, y + tail_h/2)
    p.lineTo(x + width - head_l, y + tail_h/2)
    p.lineTo(x + width - head_l, y + height/2)
    p.lineTo(x + width, y)
    p.lineTo(x + width - head_l, y - height/2)
    p.lineTo(x + width - head_l, y - tail_h/2)
    p.lineTo(x + head_l, y - tail_h/2)
    p.lineTo(x + head_l, y - height/2)
    p.lineTo(x, y)
    p.lineTo(x + head_l, y + height/2)
    p.close()
    c.drawPath(p, fill=1, stroke=1)

def get_display_name(client):
    name = client.get('name', 'Sample Client')
    if client.get('is_joint') and client.get('spouse_name'):
        spouse = client.get('spouse_name')
        parts1 = name.split(' ')
        first1 = parts1[0]
        last = ' '.join(parts1[1:]) if len(parts1) > 1 else ''
        
        parts2 = spouse.split(' ')
        first2 = parts2[0]
        last2 = ' '.join(parts2[1:]) if len(parts2) > 1 else ''
        
        final_last = last if last else last2
        
        if final_last:
            return f"{first1} & {first2} {final_last}".strip()
        else:
            return f"{first1} & {first2}".strip()
    return name

def generate_sacs(filepath, data):
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    client = data['client']
    calc = data['calculations']
    
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height - 40, "Simple Automated Cashflow System (SACS)")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 60, "Client Example")
    
    # ------------------ TOP SECTION ------------------
    c.saveState()
    c.translate(0, height * 0.35) 
    c.scale(0.8, 0.8)
    local_height = height - 20
    
    c.setFont("Helvetica-Bold", 48)
    c.setFillColor(colors.HexColor("#28a745"))
    c.drawString(100, local_height - 100, "$")
    c.setFont("Helvetica", 9)
    if client.get('salary_client1', 0) > 0:
        c.drawString(80, local_height - 120, f"${client.get('salary_client1', 0):,.0f} - Client 1")
    if client.get('salary_client2', 0) > 0:
        c.drawString(80, local_height - 135, f"${client.get('salary_client2', 0):,.0f} - Client 2")
    
    draw_custom_arrow(c, [(95, local_height - 145), (110, local_height - 145), (110, local_height - 160), (125, local_height - 160), (102.5, local_height - 180), (80, local_height - 160), (95, local_height - 160)], color=colors.black, fill_color=colors.HexColor("#28a745"))
    
    inflow_x, inflow_y = 200, local_height - 250
    c.setFillColor(colors.HexColor("#4cae4c"))
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.circle(inflow_x, inflow_y, 75, fill=1, stroke=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(inflow_x, inflow_y + 30, "INFLOW")
    
    c.setFillColor(colors.white)
    c.rect(inflow_x - 45, inflow_y - 15, 90, 25, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#4cae4c"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(inflow_x, inflow_y - 6, f"${calc['inflow']:,.0f}")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(inflow_x, inflow_y - 65, "$1,000 Floor")
    
    outflow_x, outflow_y = 450, local_height - 250
    c.setFillColor(colors.HexColor("#d9534f"))
    c.circle(outflow_x, outflow_y, 75, fill=1, stroke=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(outflow_x, outflow_y + 30, "OUTFLOW")
    
    c.rect(outflow_x - 45, outflow_y - 15, 90, 25, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#d9534f"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(outflow_x, outflow_y - 6, f"${calc['outflow']:,.0f}")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(outflow_x, outflow_y - 65, "$1,000 Floor")
    
    draw_block_arrow(c, inflow_x + 85, inflow_y, 80, 40, direction="right", color=colors.HexColor("#d9534f"), fill_color=colors.white)
    c.setFillColor(colors.HexColor("#d9534f"))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(inflow_x + 125, inflow_y - 3, f"X = ${calc['outflow']:,.0f}/month*")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 6)
    c.drawCentredString(inflow_x + 125, inflow_y - 30, "Automated transfer on the 28th")
    
    p = c.beginPath()
    ax, ay = inflow_x, inflow_y - 80
    c.setStrokeColor(colors.HexColor("#5bc0de"))
    c.setFillColor(colors.white)
    c.setLineWidth(1)
    p.moveTo(ax - 10, ay)
    p.lineTo(ax + 10, ay)
    p.lineTo(ax + 10, ay - 60)
    p.lineTo(ax + 40, ay - 60)
    p.lineTo(ax + 40, ay - 50)
    p.lineTo(ax + 60, ay - 70)
    p.lineTo(ax + 40, ay - 90)
    p.lineTo(ax + 40, ay - 80)
    p.lineTo(ax - 10, ay - 80)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#5bc0de"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(ax + 25, ay - 74, f"${calc['excess']:,.0f}/mo*")

    pr_x, pr_y = 325, local_height - 420
    c.setFillColor(colors.HexColor("#428bca"))
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.circle(pr_x, pr_y, 75, fill=1, stroke=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(pr_x, pr_y + 25, "PRIVATE")
    c.drawCentredString(pr_x, pr_y + 10, "RESERVE")
    
    c.setFillColor(colors.pink)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.circle(pr_x, pr_y - 25, 20, fill=1, stroke=1)
    c.circle(pr_x - 20, pr_y - 25, 8, fill=1, stroke=1) 
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(pr_x, pr_y - 95, "MONTHLY CASHFLOW")
    
    c.setStrokeColor(colors.HexColor("#428bca"))
    c.setDash(4, 4)
    c.line(pr_x, pr_y - 100, pr_x, local_height - 550)
    c.setDash()
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)
    c.drawCentredString(540, local_height - 160, "X = Monthly")
    c.drawCentredString(540, local_height - 170, "Expenses")
    
    c.setLineWidth(1)
    p = c.beginPath()
    p.moveTo(540, local_height - 180)
    p.lineTo(540, outflow_y - 6)
    p.lineTo(outflow_x + 45, outflow_y - 6)
    c.drawPath(p, fill=0, stroke=1)
    
    c.restoreState()
    
    # ------------------ BOTTOM SECTION ------------------
    c.saveState()
    c.translate(0, 150)
    c.scale(0.8, 0.8)
    
    fica_x, fica_y = 250, height - 600
    inv_x, inv_y = 450, height - 600
    
    c.setFillColor(colors.HexColor("#b3d4fc"))
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.circle(fica_x, fica_y, 75, fill=1, stroke=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(fica_x, fica_y + 20, "FICA")
    c.drawCentredString(fica_x, fica_y + 5, "ACCOUNT")
    
    c.rect(fica_x - 40, fica_y - 25, 80, 20, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#428bca"))
    c.setFont("Helvetica", 10)
    
    fica_balance = 0
    inv_balance = 0
    accounts = client.get('accounts', [])
    for a in accounts:
        name_lower = (a.get('institution', '') + " " + a.get('acc_type', '')).lower()
        if 'fica' in name_lower or 'private reserve' in name_lower:
            fica_balance += a.get('last_known_balance', 0)
        elif a.get('category') == 'non_retirement' and ('invest' in name_lower or 'brokerage' in name_lower):
            inv_balance += a.get('last_known_balance', 0)
    
    if fica_balance == 0:
        fica_balance = calc.get('private_reserve_target', 0)
    
    c.drawCentredString(fica_x, fica_y - 19, f"${fica_balance:,.0f}")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)
    c.drawCentredString(fica_x, fica_y - 90, "6X Monthly Expenses + Deductibles")
    
    c.setFillColor(colors.HexColor("#1b365d"))
    c.circle(inv_x, inv_y, 75, fill=1, stroke=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(inv_x, inv_y + 20, "INVESTMENT")
    c.drawCentredString(inv_x, inv_y + 5, "ACCOUNT")
    
    c.rect(inv_x - 40, inv_y - 25, 80, 20, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1b365d"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(inv_x, inv_y - 19, f"${inv_balance:,.0f}+")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)
    c.drawCentredString(inv_x, inv_y - 90, "Remainder")
    
    draw_double_arrow(c, 350, height - 600, 50, 20, color=colors.black, fill_color=colors.HexColor("#5bc0de"))
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, height - 720, "LONG TERM CASHFLOW")
    c.setFillColor(colors.HexColor("#428bca"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 735, "(Magnified Private Reserve Cashflow)")
    
    c.restoreState()
    
    c.showPage()
    c.save()


def generate_tcc(filepath, data):
    c = canvas.Canvas(filepath, pagesize=landscape(letter))
    width, height = landscape(letter)
    client = data['client']
    calc = data['calculations']
    accounts = client.get('accounts', [])
    report_date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    def draw_account_circle(x, y, acc):
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.gray)
        c.setLineWidth(1)
        r = 45
        c.circle(x, y, r, fill=1, stroke=1)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 8)
        
        last4 = f" *{acc.get('last4')}" if acc.get('last4') else ""
        c.drawCentredString(x, y + 20, "ACCT #" + last4)
        c.drawCentredString(x, y + 10, acc.get('institution', ''))
        c.drawCentredString(x, y, acc.get('acc_type', ''))
        
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x, y - 10, f"${acc.get('last_known_balance', 0):,.2f}")
        c.setFont("Helvetica", 7)
        c.drawCentredString(x, y - 22, f"a/o {report_date}")
        
        if acc.get('cash_balance', 0) > 0:
            c.circle(x, y - 30, 15, fill=0, stroke=1)
            c.setFont("Helvetica", 7)
            c.drawCentredString(x, y - 27, f"${acc.get('cash_balance'):,.0f}")
            c.drawCentredString(x, y - 34, "Cash")

    c.setFont("Helvetica", 10)
    c.drawString(30, height - 30, "NAME:")
    c.drawString(30, height - 45, "DATE:")
    c.line(70, height - 30, 250, height - 30)
    c.line(70, height - 45, 250, height - 45)
    
    display_name = get_display_name(client)
    c.drawString(75, height - 28, display_name)
    c.drawString(75, height - 43, report_date)
    
    c.setFillColor(colors.gray)
    c.rect(width/2 - 70, height - 50, 140, 40, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, height - 25, "GRAND TOTAL")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, height - 40, f"${calc['grand_total']:,.2f}")
    
    c.setStrokeColor(colors.HexColor("#7c9c3d")) 
    c.setLineWidth(1)
    c.line(20, height/2 + 20, width - 20, height/2 + 20)
    c.setStrokeColor(colors.lightgrey)
    c.line(width/2, height - 60, width/2, 20)
    
    c.setFillColor(colors.HexColor("#7c9c3d"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, height/2 + 25, "RETIREMENT")
    c.drawRightString(width - 30, height/2 + 25, "RETIREMENT")
    
    c.setFillColor(colors.gray)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, height/2 - 10, "NON")
    c.drawString(30, height/2 - 22, "RETIREMENT")
    c.drawRightString(width - 30, height/2 - 10, "NON")
    c.drawRightString(width - 30, height/2 - 22, "RETIREMENT")

    # Client 1
    c.setFillColor(colors.gray)
    c.rect(20, height - 120, 150, 35, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(95, height - 100, "Client 1 Retirement")
    c.drawCentredString(95, height - 112, f"${calc['ret_client1_total']:,.2f}")
    
    c.setFillColor(colors.HexColor("#6b8e23"))
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.ellipse(180, height - 130, 260, height - 50, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(220, height - 80, "Client 1")
    c.setFont("Helvetica", 8)
    c.drawCentredString(220, height - 92, f"Age: {client.get('age', '')}")
    c.drawCentredString(220, height - 102, f"DOB: {client.get('dob', '')}")
    c.drawCentredString(220, height - 112, f"SSN: ***-**-{client.get('ssn_last4', '')}")

    # Client 2
    c.setFillColor(colors.gray)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(width - 170, height - 120, 150, 35, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width - 95, height - 100, "Client 2 Retirement")
    c.drawCentredString(width - 95, height - 112, f"${calc['ret_client2_total']:,.2f}")
    
    c.setFillColor(colors.HexColor("#6b8e23"))
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.ellipse(width - 260, height - 130, width - 180, height - 50, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width - 220, height - 80, "Client 2")
    c.setFont("Helvetica", 8)
    c.drawCentredString(width - 220, height - 92, f"Age: {client.get('spouse_age', '')}")
    c.drawCentredString(width - 220, height - 102, f"DOB: {client.get('spouse_dob', '')}")
    c.drawCentredString(width - 220, height - 112, f"SSN: ***-**-{client.get('spouse_ssn_last4', '')}")

    c.setFillColor(colors.lightgrey)
    c.setStrokeColor(colors.gray)
    c.setLineWidth(1)
    c.rect(width/2 - 70, height - 90, 140, 30, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height - 75, f"Liabilities: ${calc['liabilities_total']:,.2f}")
    c.drawCentredString(width/2, height - 85, f"a/o {report_date}")

    ret1 = [a for a in accounts if a['category'] == 'retirement' and a['owner'] == 'client1']
    ret2 = [a for a in accounts if a['category'] == 'retirement' and a['owner'] == 'client2']
    non_ret = [a for a in accounts if a['category'] == 'non_retirement']
    trust = [a for a in accounts if a['category'] == 'trust']
    liab = [a for a in accounts if a['category'] == 'liability']
    
    start_y = height - 200
    x_positions_ret1 = [120, 230, 340]
    for i, acc in enumerate(ret1[:3]):
        draw_account_circle(x_positions_ret1[i], start_y, acc)
        
    x_positions_ret2 = [width/2 + 60, width/2 + 170, width/2 + 280]
    for i, acc in enumerate(ret2[:3]):
        draw_account_circle(x_positions_ret2[i], start_y, acc)

    if trust:
        trust_acc = trust[0]
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.gray)
        c.circle(width/2, height/2 - 30, 70, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        inst = trust_acc.get('institution', 'Family Trust')
        act = trust_acc.get('acc_type', '')
        c.drawCentredString(width/2, height/2 - 5, inst)
        if act and act.lower() not in inst.lower():
            c.drawCentredString(width/2, height/2 - 17, act)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, height/2 - 35, f"${trust_acc.get('last_known_balance', 0):,.2f}")
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, height/2 - 50, f"a/o {report_date}")

    nr_left = non_ret[:len(non_ret)//2 + len(non_ret)%2]
    nr_right = non_ret[len(non_ret)//2 + len(non_ret)%2:]
    
    nr_y1, nr_y2 = height/2 - 80, height/2 - 190
    nr_left_pos = [(120, nr_y1), (230, nr_y1), (120, nr_y2), (230, nr_y2)]
    for i, acc in enumerate(nr_left[:4]):
        draw_account_circle(nr_left_pos[i][0], nr_left_pos[i][1], acc)
        
    nr_right_pos = [(width - 120, nr_y1), (width - 120, nr_y2), (width - 230, nr_y1), (width - 230, nr_y2)]
    for i, acc in enumerate(nr_right[:4]):
        draw_account_circle(nr_right_pos[i][0], nr_right_pos[i][1], acc)

    c.setFillColor(colors.lightgrey)
    c.rect(width/2 - 100, 50, 200, 120, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, 155, "Liabilities:")
    c.setLineWidth(0.5)
    c.line(width/2 - 80, 150, width/2 + 80, 150)
    
    y_liab = 135
    for acc in liab[:8]:
        nm = acc.get('institution', '') + " " + acc.get('acc_type', '')
        c.drawString(width/2 - 90, y_liab, nm[:20])
        c.drawRightString(width/2 + 90, y_liab, f"${acc.get('last_known_balance', 0):,.2f}")
        y_liab -= 12

    c.setFillColor(colors.gray)
    c.rect(width/2 - 100, 10, 200, 35, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width/2, 30, "NON RETIREMENT TOTAL")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, 17, f"${calc['non_ret_total']:,.2f}")

    c.setFillColor(colors.red)
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 30, 20, "* Indicates we do not have up to date information")

    c.showPage()
    c.save()
