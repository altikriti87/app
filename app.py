<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>النظام المحاسبي المتكامل</title>
    <style>
        :root { 
            --primary: #2c3e50; 
            --secondary: #3498db; 
            --success: #27ae60; 
            --danger: #e74c3c;
            --warning: #f39c12;
            --info: #17a2b8;
        }
        
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            background-color: #f4f7f6; 
            margin: 0;
            padding: 20px;
        }
        
        .container { 
            max-width: 1400px; 
            margin: auto; 
            background: white; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
        }
        
        .tabs { 
            display: flex; 
            background: var(--primary); 
            border-radius: 8px 8px 0 0;
            overflow: hidden;
            margin-bottom: 0;
        }
        
        .tab { 
            padding: 15px 25px; 
            color: white; 
            cursor: pointer; 
            border-right: 1px solid rgba(255,255,255,0.1);
            transition: background 0.3s;
        }
        
        .tab:hover, .tab.active { 
            background: var(--secondary); 
        }
        
        .tab-content { 
            display: none; 
            padding: 20px; 
            border: 2px solid var(--primary);
            border-top: none;
            border-radius: 0 0 8px 8px;
            background: white;
        }
        
        .tab-content.active { 
            display: block; 
        }
        
        .entry-section { 
            background: #fff; 
            border: 2px solid var(--secondary); 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
        }
        
        .row-input { 
            display: grid; 
            grid-template-columns: 3fr 1fr 1fr 0.5fr; 
            gap: 10px; 
            margin-bottom: 10px; 
            align-items: center; 
        }
        
        input, textarea, select { 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 6px; 
            width: 100%; 
            box-sizing: border-box; 
            font-size: 14px;
        }
        
        textarea { 
            resize: vertical; 
            margin-top: 10px; 
            border-color: var(--secondary); 
            min-height: 80px;
        }
        
        .db-controls { 
            background: #ecf0f1; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            display: flex; 
            gap: 10px; 
            flex-wrap: wrap; 
        }
        
        .btn { 
            padding: 10px 15px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-weight: bold; 
            color: white; 
            font-size: 14px;
            transition: opacity 0.3s;
        }
        
        .btn:hover { opacity: 0.9; }
        .btn-save { background: var(--success); }
        .btn-export { background: #2c3e50; }
        .btn-clear { background: var(--danger); }
        .btn-secondary { background: var(--secondary); }
        .btn-warning { background: var(--warning); }
        .btn-info { background: var(--info); }
        
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 15px; 
            font-size: 14px;
        }
        
        th, td { 
            border: 1px solid #dee2e6; 
            padding: 10px; 
            text-align: center; 
        }
        
        th { 
            background: var(--primary); 
            color: white; 
            position: sticky;
            top: 0;
        }
        
        .description-cell { 
            background: #fffdf0; 
            font-style: italic; 
            color: #555; 
            text-align: right !important; 
            padding-right: 30px !important; 
            font-size: 0.9em; 
        }
        
        .t-container { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 15px; 
            margin: 20px 0; 
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
        }
        
        .t-account { 
            border: 2px solid var(--primary); 
            width: 220px; 
            background: white;
            flex-shrink: 0;
        }
        
        .t-head { 
            background: var(--primary); 
            color: white; 
            text-align: center; 
            padding: 5px; 
            font-weight: bold;
        }
        
        .t-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            min-height: 50px; 
            font-size: 0.8em; 
        }
        
        .side { 
            padding: 5px; 
            border-left: 1px solid #eee; 
            min-height: 40px;
        }
        
        .t-foot { 
            background: #eee; 
            border-top: 1px solid var(--primary); 
            text-align: center; 
            font-weight: bold;
            padding: 5px;
        }
        
        .account-search { 
            margin: 15px 0; 
            position: relative; 
        }
        
        .financial-statement {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid var(--info);
        }
        
        .statement-table {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .statement-header {
            background: var(--info);
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .statement-row {
            display: flex;
            justify-content: space-between;
            padding: 12px 20px;
            border-bottom: 1px solid #eee;
        }
        
        .statement-row.total {
            background: var(--success);
            color: white;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .statement-row.subtotal {
            background: #e8f4f8;
            font-weight: bold;
        }
        
        .account-editor {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid var(--warning);
        }
        
        .editor-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .account-item {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 5px 0;
            background: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .account-type {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            color: white;
            margin-right: 10px;
        }
        
        .type-asset { background: #3498db; }
        .type-liability { background: #e74c3c; }
        .type-equity { background: #9b59b6; }
        .type-revenue { background: #27ae60; }
        .type-expense { background: #f39c12; }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            width: 500px;
            max-width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-top: 4px solid var(--primary);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--primary);
            margin: 10px 0;
        }
        
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            font-weight: bold;
        }
        
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .alert-info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    </style>
</head>
<body>

<div class="container">
    <h1 style="text-align: center; color: var(--primary); margin-bottom: 30px;">النظام المحاسبي المتكامل</h1>
    
    <div class="tabs">
        <div class="tab active" onclick="showTab('entry')">القيد اليومي</div>
        <div class="tab" onclick="showTab('journal')">دفتر اليومية</div>
        <div class="tab" onclick="showTab('ledger')">دفتر الأستاذ</div>
        <div class="tab" onclick="showTab('trial')">ميزان المراجعة</div>
        <div class="tab" onclick="showTab('financial')">القوائم المالية</div>
        <div class="tab" onclick="showTab('accounts')">إدارة الحسابات</div>
        <div class="tab" onclick="showTab('closing')">إقفال الحسابات</div>
    </div>
    
    <!-- ============ تبويب القيد اليومي ============ -->
    <div id="entry-tab" class="tab-content active">
        <div class="db-controls">
            <button class="btn btn-export" onclick="exportData()">⬇️ تصدير البيانات</button>
            <button class="btn btn-clear" onclick="resetAllData()">⚠️ تصفير البيانات</button>
            <button class="btn btn-info" onclick="showStats()">📊 الإحصائيات</button>
        </div>
        
        <div class="entry-section">
            <h3 style="color: var(--secondary);">إدخال قيد جديد</h3>
            
            <div class="account-search">
                <input type="text" id="accountSearch" placeholder="🔍 ابحث عن حساب..." 
                       oninput="searchAccounts()" style="margin-bottom: 15px;">
                <div id="searchResults" style="max-height: 200px; overflow-y: auto; border: 1px solid #ddd; border-radius: 5px; display: none;"></div>
            </div>
            
            <div id="entryRows">
                <div class="row-input">
                    <select class="acc-select" onchange="updateAccountName(this)">
                        <option value="">اختر حساب...</option>
                    </select>
                    <input type="number" placeholder="مدين" class="acc-debit" oninput="validate()" min="0" step="0.01">
                    <input type="number" placeholder="دائن" class="acc-credit" oninput="validate()" min="0" step="0.01">
                    <button onclick="removeRow(this)" class="btn btn-clear">X</button>
                </div>
            </div>
            
            <button class="btn btn-secondary" onclick="addRow()" style="margin: 10px 0;">+ إضافة حساب آخر</button>
            
            <textarea id="entryDesc" placeholder="شرح القيد المحاسبي..."></textarea>
            
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button id="submitBtn" class="btn btn-save" onclick="saveEntry()" disabled>💾 حفظ القيد</button>
                <button class="btn btn-clear" onclick="clearEntryForm()">🗑️ مسح النموذج</button>
            </div>
            
            <div id="entryMessage"></div>
        </div>
    </div>
    
    <!-- ============ تبويب دفتر اليومية ============ -->
    <div id="journal-tab" class="tab-content">
        <h2 style="color: var(--secondary);">دفتر اليومية العامة</h2>
        <div style="overflow-x: auto;">
            <table id="journalTable">
                <thead>
                    <tr>
                        <th width="5%">#</th>
                        <th width="15%">التاريخ</th>
                        <th width="40%">الحساب / البيان</th>
                        <th width="15%">مدين</th>
                        <th width="15%">دائن</th>
                        <th width="10%">الإجراءات</th>
                    </tr>
                </thead>
                <tbody></tbody>
                <tfoot>
                    <tr style="background: #f8f9fa; font-weight: bold;">
                        <td colspan="3">الإجمالي</td>
                        <td id="journalTotalDebit">0.00</td>
                        <td id="journalTotalCredit">0.00</td>
                        <td></td>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>
    
    <!-- ============ تبويب دفتر الأستاذ ============ -->
    <div id="ledger-tab" class="tab-content">
        <h2 style="color: var(--secondary);">دفتر الأستاذ</h2>
        <div id="ledgerArea" class="t-container"></div>
    </div>
    
    <!-- ============ تبويب ميزان المراجعة ============ -->
    <div id="trial-tab" class="tab-content">
        <h2 style="color: var(--secondary);">ميزان المراجعة</h2>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th width="50%">الحساب</th>
                        <th width="25%">مدين</th>
                        <th width="25%">دائن</th>
                    </tr>
                </thead>
                <tbody id="trialBody"></tbody>
                <tfoot style="background: var(--success); color: white; font-weight: bold;">
                    <tr>
                        <td>الإجمالي</td>
                        <td id="totalD">0.00</td>
                        <td id="totalC">0.00</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>
    
    <!-- ============ تبويب القوائم المالية ============ -->
    <div id="financial-tab" class="tab-content">
        <div class="db-controls">
            <button class="btn btn-info" onclick="generateFinancialStatements()">🔄 تحديث القوائم</button>
            <button class="btn btn-export" onclick="exportFinancialStatements()">📄 تصدير القوائم</button>
            <button class="btn btn-warning" onclick="closeTemporaryAccounts()">🔒 إقفال مؤقت</button>
        </div>
        
        <!-- قائمة الدخل -->
        <div class="financial-statement">
            <div class="statement-header">قائمة الدخل</div>
            <div id="incomeStatement" class="statement-table">
                <div class="statement-row">
                    <span>الإيرادات:</span>
                    <span id="totalRevenue">0.00</span>
                </div>
                <div class="statement-row">
                    <span>المصاريف:</span>
                    <span id="totalExpenses">0.00</span>
                </div>
                <div id="netIncomeRow" class="statement-row total">
                    <span>صافي الربح/الخسارة:</span>
                    <span id="netIncome">0.00</span>
                </div>
            </div>
        </div>
        
        <!-- الميزانية العمومية -->
        <div class="financial-statement">
            <div class="statement-header">الميزانية العمومية</div>
            <div id="balanceSheet" class="statement-table">
                <div class="statement-row subtotal">
                    <span>الموجودات:</span>
                    <span id="totalAssets">0.00</span>
                </div>
                <div style="margin-right: 20px;">
                    <div class="statement-row">
                        <span style="margin-right: 20px;">• الموجودات المتداولة</span>
                        <span id="currentAssets">0.00</span>
                    </div>
                    <div class="statement-row">
                        <span style="margin-right: 20px;">• الموجودات الثابتة</span>
                        <span id="fixedAssets">0.00</span>
                    </div>
                </div>
                
                <div class="statement-row subtotal">
                    <span>الالتزامات وحقوق الملكية:</span>
                    <span id="totalLiabilitiesEquity">0.00</span>
                </div>
                <div style="margin-right: 20px;">
                    <div class="statement-row">
                        <span style="margin-right: 20px;">• المطلوبات</span>
                        <span id="totalLiabilities">0.00</span>
                    </div>
                    <div class="statement-row">
                        <span style="margin-right: 20px;">• حقوق الملكية</span>
                        <span id="totalEquity">0.00</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- قائمة التدفقات النقدية -->
        <div class="financial-statement">
            <div class="statement-header">قائمة التدفقات النقدية</div>
            <div id="cashFlowStatement" class="statement-table">
                <div class="statement-row">
                    <span>التدفق النقدي من الأنشطة التشغيلية:</span>
                    <span id="operatingCashFlow">0.00</span>
                </div>
                <div class="statement-row">
                    <span>التدفق النقدي من الأنشطة الاستثمارية:</span>
                    <span id="investingCashFlow">0.00</span>
                </div>
                <div class="statement-row">
                    <span>التدفق النقدي من الأنشطة التمويلية:</span>
                    <span id="financingCashFlow">0.00</span>
                </div>
                <div class="statement-row total">
                    <span>صافي التدفق النقدي:</span>
                    <span id="netCashFlow">0.00</span>
                </div>
                <div class="statement-row subtotal">
                    <span>الرصيد النقدي في بداية الفترة:</span>
                    <span id="beginningCash">0.00</span>
                </div>
                <div class="statement-row total">
                    <span>الرصيد النقدي في نهاية الفترة:</span>
                    <span id="endingCash">0.00</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- ============ تبويب إدارة الحسابات ============ -->
    <div id="accounts-tab" class="tab-content">
        <h2 style="color: var(--secondary);">إدارة دليل الحسابات</h2>
        
        <div class="account-editor">
            <h3>إضافة/تعديل حساب</h3>
            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px;">
                <input type="text" id="newAccountName" placeholder="اسم الحساب الجديد">
                <select id="newAccountType">
                    <option value="">اختر النوع...</option>
                    <option value="asset">موجودات</option>
                    <option value="liability">مطلوبات</option>
                    <option value="equity">حقوق ملكية</option>
                    <option value="revenue">إيرادات</option>
                    <option value="expense">مصاريف</option>
                </select>
                <div style="display: flex; gap: 10px;">
                    <button class="btn btn-save" onclick="addNewAccount()">➕ إضافة</button>
                    <button class="btn btn-clear" onclick="clearAccountForm()">🗑️ مسح</button>
                </div>
            </div>
            
            <div id="accountsList" style="margin-top: 20px; max-height: 400px; overflow-y: auto;">
                <!-- سيتم ملئها تلقائياً -->
            </div>
        </div>
    </div>
    
    <!-- ============ تبويب إقفال الحسابات ============ -->
    <div id="closing-tab" class="tab-content">
        <h2 style="color: var(--secondary);">إقفال الحسابات المؤقتة</h2>
        
        <div class="alert alert-info">
            <strong>ملاحظة:</strong> سيتم إقفال حسابات الإيرادات والمصاريف وإرسال صافي الربح/الخسارة إلى حقوق الملكية
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div>إجمالي الإيرادات</div>
                <div class="stat-value" id="closingRevenue">0.00</div>
            </div>
            <div class="stat-card">
                <div>إجمالي المصاريف</div>
                <div class="stat-value" id="closingExpenses">0.00</div>
            </div>
            <div class="stat-card">
                <div>صافي الربح/الخسارة</div>
                <div class="stat-value" id="closingNet">0.00</div>
            </div>
        </div>
        
        <button class="btn btn-warning" onclick="performClosing()" style="width: 100%; padding: 15px; font-size: 1.1em;">
            🔐 إقفال حسابات الفترة وإعداد القوائم الختامية
        </button>
        
        <div id="closingResults" style="margin-top: 20px;"></div>
    </div>
</div>

<!-- ============ نافذة الإحصائيات ============ -->
<div id="statsModal" class="modal">
    <div class="modal-content">
        <h2 style="color: var(--primary); text-align: center;">إحصائيات النظام</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div>عدد القيود</div>
                <div class="stat-value" id="statEntries">0</div>
            </div>
            <div class="stat-card">
                <div>عدد الحسابات</div>
                <div class="stat-value" id="statAccounts">0</div>
            </div>
            <div class="stat-card">
                <div>إجمالي المدين</div>
                <div class="stat-value" id="statTotalDebit">0.00</div>
            </div>
            <div class="stat-card">
                <div>إجمالي الدائن</div>
                <div class="stat-value" id="statTotalCredit">0.00</div>
            </div>
        </div>
        <button class="btn btn-clear" onclick="closeModal('statsModal')" style="width: 100%; margin-top: 20px;">إغلاق</button>
    </div>
</div>

<script>
    // ============ نظام الحسابات الأساسي ============
    let accounts = JSON.parse(localStorage.getItem('accounting_accounts')) || [
        { id: 1, name: "نقدية بالصندوق", type: "asset" },
        { id: 2, name: "بنك", type: "asset" },
        { id: 3, name: "مدينون", type: "asset" },
        { id: 4, name: "مخزون", type: "asset" },
        { id: 5, name: "أثاث ومعدات", type: "asset" },
        { id: 6, name: "مباني", type: "asset" },
        { id: 7, name: "دائنون", type: "liability" },
        { id: 8, name: "قروض", type: "liability" },
        { id: 9, name: "رأس المال", type: "equity" },
        { id: 10, name: "أرباح محتجزة", type: "equity" },
        { id: 11, name: "مبيعات", type: "revenue" },
        { id: 12, name: "إيرادات خدمات", type: "revenue" },
        { id: 13, name: "مشتريات", type: "expense" },
        { id: 14, name: "رواتب وأجور", type: "expense" },
        { id: 15, name: "إيجار", type: "expense" },
        { id: 16, name: "كهرباء وماء", type: "expense" },
        { id: 17, name: "صيانة", type: "expense" },
        { id: 18, name: "مصاريف تسويق", type: "expense" },
        { id: 19, name: "مصاريف إدارية", type: "expense" },
        { id: 20, name: "مصاريف إهلاك", type: "expense" }
    ];

    let allEntries = JSON.parse(localStorage.getItem('accounting_entries')) || [];
    let closingEntries = JSON.parse(localStorage.getItem('closing_entries')) || [];

    // ============ تهيئة النظام ============
    window.onload = function() {
        updateAccountSelect();
        renderAccountsList();
        showTab('entry');
        validate();
    };

    // ============ إدارة التبويبات ============
    function showTab(tabName) {
        // إخفاء كل المحتويات
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // إزالة النشاط من كل التبويبات
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // إظهار المحتوى المطلوب
        document.getElementById(tabName + '-tab').classList.add('active');
        
        // تفعيل التبويب
        event.target.classList.add('active');
        
        // تحديث البيانات في التبويب
        switch(tabName) {
            case 'journal':
                renderJournal();
                break;
            case 'ledger':
                renderLedger();
                break;
            case 'trial':
                renderTrialBalance();
                break;
            case 'financial':
                generateFinancialStatements();
                break;
            case 'accounts':
                renderAccountsList();
                break;
            case 'closing':
                updateClosingStats();
                break;
        }
    }

    // ============ إدارة الحسابات ============
    function updateAccountSelect() {
        const select = document.querySelector('.acc-select');
        select.innerHTML = '<option value="">اختر حساب...</option>';
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.id;
            option.textContent = account.name;
            option.setAttribute('data-type', account.type);
            select.appendChild(option);
        });
    }

    function searchAccounts() {
        const searchTerm = document.getElementById('accountSearch').value.toLowerCase();
        const resultsDiv = document.getElementById('searchResults');
        
        if (searchTerm.length < 1) {
            resultsDiv.style.display = 'none';
            return;
        }
        
        const filtered = accounts.filter(acc => 
            acc.name.toLowerCase().includes(searchTerm)
        );
        
        if (filtered.length === 0) {
            resultsDiv.innerHTML = '<div style="padding: 10px; color: #666;">لا توجد نتائج</div>';
            resultsDiv.style.display = 'block';
            return;
        }
        
        resultsDiv.innerHTML = filtered.map(acc => `
            <div style="padding: 8px 15px; border-bottom: 1px solid #eee; cursor: pointer; 
                 background: white;" 
                 onclick="selectAccountFromSearch(${acc.id})">
                <span>${acc.name}</span>
                <span style="float: left; font-size: 0.8em; color: #666;">${getTypeName(acc.type)}</span>
            </div>
        `).join('');
        
        resultsDiv.style.display = 'block';
    }

    function selectAccountFromSearch(accountId) {
        const account = accounts.find(acc => acc.id == accountId);
        const currentRow = document.querySelector('.row-input:last-child');
        const select = currentRow.querySelector('.acc-select');
        
        select.value = accountId;
        updateAccountName(select);
        
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('accountSearch').value = '';
        
        currentRow.querySelector('.acc-debit').focus();
    }

    function updateAccountName(select) {
        const accountId = select.value;
        const account = accounts.find(acc => acc.id == accountId);
        if (account) {
            // يمكن إضافة أي معلومات إضافية هنا
        }
    }

    function getTypeName(type) {
        const typeNames = {
            'asset': 'موجودات',
            'liability': 'مطلوبات',
            'equity': 'حقوق ملكية',
            'revenue': 'إيرادات',
            'expense': 'مصاريف'
        };
        return typeNames[type] || type;
    }

    function addNewAccount() {
        const name = document.getElementById('newAccountName').value.trim();
        const type = document.getElementById('newAccountType').value;
        
        if (!name || !type) {
            alert('يرجى إدخال اسم الحساب واختيار النوع');
            return;
        }
        
        // التحقق من عدم تكرار الاسم
        if (accounts.some(acc => acc.name === name)) {
            alert('اسم الحساب موجود مسبقاً');
            return;
        }
        
        const newId = accounts.length > 0 ? Math.max(...accounts.map(acc => acc.id)) + 1 : 1;
        accounts.push({ id: newId, name: name, type: type });
        
        saveAccounts();
        updateAccountSelect();
        renderAccountsList();
        
        document.getElementById('newAccountName').value = '';
        document.getElementById('newAccountType').value = '';
        
        showMessage('تم إضافة الحساب بنجاح', 'success');
    }

    function deleteAccount(accountId) {
        if (!confirm('هل أنت متأكد من حذف هذا الحساب؟ لا يمكن التراجع عن هذا الإجراء.')) {
            return;
        }
        
        // التحقق من عدم وجود قيود مرتبطة بهذا الحساب
        const hasEntries = allEntries.some(entry => 
            entry.items.some(item => item.accountId == accountId)
        );
        
        if (hasEntries) {
            alert('لا يمكن حذف الحساب لأنه مرتبط بقيود محاسبية');
            return;
        }
        
        accounts = accounts.filter(acc => acc.id != accountId);
        saveAccounts();
        updateAccountSelect();
        renderAccountsList();
        
        showMessage('تم حذف الحساب بنجاح', 'success');
    }

    function renderAccountsList() {
        const container = document.getElementById('accountsList');
        const grouped = {};
        
        accounts.forEach(account => {
            if (!grouped[account.type]) grouped[account.type] = [];
            grouped[account.type].push(account);
        });
        
        let html = '';
        
        Object.keys(grouped).forEach(type => {
            html += `<div style="margin-bottom: 20px;">
                <h4 style="color: var(--primary); border-bottom: 2px solid #eee; padding-bottom: 5px;">
                    ${getTypeName(type)}
                </h4>`;
            
            grouped[type].forEach(account => {
                html += `
                <div class="account-item">
                    <div>
                        <span class="account-type type-${account.type}">${getTypeName(account.type)}</span>
                        ${account.name}
                    </div>
                    <button onclick="deleteAccount(${account.id})" class="btn btn-clear" style="padding: 5px 10px; font-size: 12px;">
                        حذف
                    </button>
                </div>`;
            });
            
            html += '</div>';
        });
        
        container.innerHTML = html;
    }

    // ============ إدارة القيود ============
    function addRow() {
        const div = document.createElement('div');
        div.className = 'row-input';
        div.innerHTML = `
            <select class="acc-select" onchange="updateAccountName(this)">
                <option value="">اختر حساب...</option>
                ${accounts.map(acc => `<option value="${acc.id}">${acc.name}</option>`).join('')}
            </select>
            <input type="number" placeholder="مدين" class="acc-debit" oninput="validate()" min="0" step="0.01">
            <input type="number" placeholder="دائن" class="acc-credit" oninput="validate()" min="0" step="0.01">
            <button onclick="removeRow(this)" class="btn btn-clear">X</button>
        `;
        document.getElementById('entryRows').appendChild(div);
    }

    function removeRow(button) {
        const rows = document.querySelectorAll('.row-input');
        if (rows.length > 1) {
            button.parentElement.remove();
            validate();
        }
    }

    function clearEntryForm() {
        document.getElementById('entryRows').innerHTML = `
            <div class="row-input">
                <select class="acc-select" onchange="updateAccountName(this)">
                    <option value="">اختر حساب...</option>
                    ${accounts.map(acc => `<option value="${acc.id}">${acc.name}</option>`).join('')}
                </select>
                <input type="number" placeholder="مدين" class="acc-debit" oninput="validate()" min="0" step="0.01">
                <input type="number" placeholder="دائن" class="acc-credit" oninput="validate()" min="0" step="0.01">
                <button onclick="removeRow(this)" class="btn btn-clear">X</button>
            </div>`;
        document.getElementById('entryDesc').value = '';
        document.getElementById('entryMessage').innerHTML = '';
        validate();
    }

    function validate() {
        let totalDebit = 0;
        let totalCredit = 0;
        let isValid = true;
        
        const rows = document.querySelectorAll('.row-input');
        
        rows.forEach(row => {
            const debit = parseFloat(row.querySelector('.acc-debit').value) || 0;
            const credit = parseFloat(row.querySelector('.acc-credit').value) || 0;
            const account = row.querySelector('.acc-select').value;
            
            totalDebit += debit;
            totalCredit += credit;
            
            if ((debit > 0 && credit > 0) || (debit === 0 && credit === 0)) {
                isValid = false;
            }
            
            if (!account) {
                isValid = false;
            }
        });
        
        const isBalanced = Math.abs(totalDebit - totalCredit) < 0.01;
        const hasMultipleRows = rows.length >= 2;
        
        document.getElementById('submitBtn').disabled = !(isValid && isBalanced && hasMultipleRows);
        
        const messageDiv = document.getElementById('entryMessage');
        if (!isBalanced) {
            messageDiv.innerHTML = `<div class="alert alert-danger">القيد غير متوازن. الفرق: ${(totalDebit - totalCredit).toFixed(2)}</div>`;
        } else if (!hasMultipleRows) {
            messageDiv.innerHTML = `<div class="alert alert-warning">يجب إضافة حسابين على الأقل</div>`;
        } else if (!isValid) {
            messageDiv.innerHTML = `<div class="alert alert-warning">يرجى التأكد من إدخال جميع البيانات بشكل صحيح</div>`;
        } else {
            messageDiv.innerHTML = `<div class="alert alert-success">القيد متوازن وجاهز للحفظ ✅</div>`;
        }
    }

    function saveEntry() {
        const rows = document.querySelectorAll('.row-input');
        const description = document.getElementById('entryDesc').value.trim();
        
        if (!description) {
            alert('يرجى إدخال شرح للقيد');
            return;
        }
        
        const entry = {
            id: Date.now(),
            date: new Date().toLocaleDateString('ar-IQ'),
            time: new Date().toLocaleTimeString('ar-IQ'),
            description: description,
            items: [],
            closing: false
        };
        
        rows.forEach(row => {
            const accountId = row.querySelector('.acc-select').value;
            const debit = parseFloat(row.querySelector('.acc-debit').value) || 0;
            const credit = parseFloat(row.querySelector('.acc-credit').value) || 0;
            const account = accounts.find(acc => acc.id == accountId);
            
            entry.items.push({
                accountId: parseInt(accountId),
                accountName: account.name,
                accountType: account.type,
                debit: debit,
                credit: credit
            });
        });
        
        allEntries.push(entry);
        saveEntries();
        clearEntryForm();
        
        showMessage('تم حفظ القيد بنجاح!', 'success');
        renderJournal();
    }

    function deleteEntry(entryId) {
        if (!confirm('هل أنت متأكد من حذف هذا القيد؟')) {
            return;
        }
        
        allEntries = allEntries.filter(entry => entry.id != entryId);
        saveEntries();
        renderJournal();
        showMessage('تم حذف القيد بنجاح', 'success');
    }

    // ============ دفتر اليومية ============
    function renderJournal() {
        const tbody = document.querySelector('#journalTable tbody');
        let totalDebit = 0;
        let totalCredit = 0;
        
        tbody.innerHTML = '';
        
        [...allEntries, ...closingEntries].forEach((entry, index) => {
            // سطر التاريخ والبيان
            const dateRow = tbody.insertRow();
            dateRow.innerHTML = `
                <td rowspan="${entry.items.length + 1}">${index + 1}</td>
                <td rowspan="${entry.items.length + 1}">
                    ${entry.date}<br>
                    <small>${entry.time || ''}</small>
                </td>
                <td colspan="3" style="text-align: right; font-weight: bold; background: #f8f9fa;">
                    ${entry.description}
                    ${entry.closing ? '<span style="color: var(--warning);"> (إقفال)</span>' : ''}
                </td>
                <td rowspan="${entry.items.length + 1}">
                    <button onclick="deleteEntry(${entry.id})" class="btn btn-clear" style="padding: 5px 10px;">
                        حذف
                    </button>
                </td>
            `;
            
            // أسطر الحسابات
            entry.items.forEach((item, itemIndex) => {
                const row = tbody.insertRow();
                totalDebit += item.debit;
                totalCredit += item.credit;
                
                row.innerHTML = `
                    <td style="text-align: right; padding-right: 30px;">
                        ${item.debit > 0 ? 'من حـ/' : 'إلى حـ/'} ${item.accountName}
                    </td>
                    <td style="color: ${item.debit > 0 ? 'green' : '#666'}">
                        ${item.debit > 0 ? item.debit.toFixed(2) : '-'}
                    </td>
                    <td style="color: ${item.credit > 0 ? '#e74c3c' : '#666'}">
                        ${item.credit > 0 ? item.credit.toFixed(2) : '-'}
                    </td>
                `;
            });
        });
        
        document.getElementById('journalTotalDebit').textContent = totalDebit.toFixed(2);
        document.getElementById('journalTotalCredit').textContent = totalCredit.toFixed(2);
    }

    // ============ دفتر الأستاذ ============
    function renderLedger() {
        const ledgerArea = document.getElementById('ledgerArea');
        const accountBalances = {};
        
        // حساب أرصدة الحسابات
        [...allEntries, ...closingEntries].forEach(entry => {
            entry.items.forEach(item => {
                if (!accountBalances[item.accountId]) {
                    accountBalances[item.accountId] = {
                        name: item.accountName,
                        type: item.accountType,
                        debits: [],
                        credits: [],
                        totalDebit: 0,
                        totalCredit: 0
                    };
                }
                
                if (item.debit > 0) {
                    accountBalances[item.accountId].debits.push({
                        amount: item.debit,
                        desc: entry.description,
                        date: entry.date
                    });
                    accountBalances[item.accountId].totalDebit += item.debit;
                }
                
                if (item.credit > 0) {
                    accountBalances[item.accountId].credits.push({
                        amount: item.credit,
                        desc: entry.description,
                        date: entry.date
                    });
                    accountBalances[item.accountId].totalCredit += item.credit;
                }
            });
        });
        
        // بناء T-Accounts
        ledgerArea.innerHTML = '';
        
        Object.keys(accountBalances).forEach(accountId => {
            const acc = accountBalances[accountId];
            const balance = acc.totalDebit - acc.totalCredit;
            
            let html = `
                <div class="t-account">
                    <div class="t-head">${acc.name}</div>
                    <div class="t-grid">
                        <div class="side">
                            <strong>مدين</strong><br>`;
            
            acc.debits.forEach(debit => {
                html += `${debit.amount.toFixed(2)}<br><small>${debit.desc}</small><br>`;
            });
            
            html += `</div><div class="side">
                        <strong>دائن</strong><br>`;
            
            acc.credits.forEach(credit => {
                html += `${credit.amount.toFixed(2)}<br><small>${credit.desc}</small><br>`;
            });
            
            html += `</div></div>
                    <div class="t-foot">
                        الرصيد: ${Math.abs(balance).toFixed(2)} 
                        ${balance > 0 ? 'مدين' : balance < 0 ? 'دائن' : 'متوازن'}
                    </div>
                </div>`;
            
            ledgerArea.innerHTML += html;
        });
    }

    // ============ ميزان المراجعة ============
    function renderTrialBalance() {
        const trialBody = document.getElementById('trialBody');
        const accountBalances = {};
        let totalDebit = 0;
        let totalCredit = 0;
        
        // حساب أرصدة الحسابات
        [...allEntries, ...closingEntries].forEach(entry => {
            entry.items.forEach(item => {
                if (!accountBalances[item.accountId]) {
                    accountBalances[item.accountId] = {
                        name: item.accountName,
                        type: item.accountType,
                        debit: 0,
                        credit: 0
                    };
                }
                
                accountBalances[item.accountId].debit += item.debit;
                accountBalances[item.accountId].credit += item.credit;
            });
        });
        
        // بناء جدول ميزان المراجعة
        trialBody.innerHTML = '';
        
        // ترتيب الحسابات حسب النوع
        const typeOrder = ['asset', 'liability', 'equity', 'revenue', 'expense'];
        
        typeOrder.forEach(type => {
            const typeAccounts = Object.values(accountBalances).filter(acc => acc.type === type);
            
            if (typeAccounts.length > 0) {
                // إضافة عنوان للنوع
                const headerRow = trialBody.insertRow();
                headerRow.innerHTML = `
                    <td colspan="3" style="background: #f8f9fa; font-weight: bold; text-align: right;">
                        ${getTypeName(type)}
                    </td>`;
                
                // إضافة الحسابات
                typeAccounts.forEach(acc => {
                    const balance = acc.debit - acc.credit;
                    
                    if (Math.abs(balance) > 0.01) {
                        const row = trialBody.insertRow();
                        const debitAmount = balance > 0 ? balance : 0;
                        const creditAmount = balance < 0 ? Math.abs(balance) : 0;
                        
                        totalDebit += debitAmount;
                        totalCredit += creditAmount;
                        
                        row.innerHTML = `
                            <td style="text-align: right; padding-right: 30px;">${acc.name}</td>
                            <td>${debitAmount > 0 ? debitAmount.toFixed(2) : '-'}</td>
                            <td>${creditAmount > 0 ? creditAmount.toFixed(2) : '-'}</td>
                        `;
                    }
                });
            }
        });
        
        document.getElementById('totalD').textContent = totalDebit.toFixed(2);
        document.getElementById('totalC').textContent = totalCredit.toFixed(2);
    }

    // ============ القوائم المالية ============
    function generateFinancialStatements() {
        const accountBalances = {};
        
        // حساب أرصدة الحسابات (باستثناء قيود الإقفال)
        allEntries.forEach(entry => {
            entry.items.forEach(item => {
                if (!accountBalances[item.accountId]) {
                    accountBalances[item.accountId] = {
                        name: item.accountName,
                        type: item.accountType,
                        debit: 0,
                        credit: 0
                    };
                }
                
                accountBalances[item.accountId].debit += item.debit;
                accountBalances[item.accountId].credit += item.credit;
            });
        });
        
        // حساب الأرقام للقوائم المالية
        let totalRevenue = 0;
        let totalExpenses = 0;
        let totalAssets = 0;
        let totalLiabilities = 0;
        let totalEquity = 0;
        let currentAssets = 0;
        let fixedAssets = 0;
        let cashBalance = 0;
        
        Object.values(accountBalances).forEach(acc => {
            const balance = acc.debit - acc.credit;
            
            switch(acc.type) {
                case 'revenue':
                    totalRevenue += Math.abs(balance);
                    break;
                case 'expense':
                    totalExpenses += Math.abs(balance);
                    break;
                case 'asset':
                    totalAssets += Math.abs(balance);
                    if (acc.name.includes('نقد') || acc.name.includes('بنك')) {
                        cashBalance += Math.abs(balance);
                        currentAssets += Math.abs(balance);
                    } else if (acc.name.includes('أثاث') || acc.name.includes('مباني') || acc.name.includes('معدات')) {
                        fixedAssets += Math.abs(balance);
                    } else {
                        currentAssets += Math.abs(balance);
                    }
                    break;
                case 'liability':
                    totalLiabilities += Math.abs(balance);
                    break;
                case 'equity':
                    totalEquity += Math.abs(balance);
                    break;
            }
        });
        
        const netIncome = totalRevenue - totalExpenses;
        
        // تحديث قائمة الدخل
        document.getElementById('totalRevenue').textContent = totalRevenue.toFixed(2);
        document.getElementById('totalExpenses').textContent = totalExpenses.toFixed(2);
        document.getElementById('netIncome').textContent = netIncome.toFixed(2);
        
        if (netIncome >= 0) {
            document.getElementById('netIncomeRow').style.background = 'var(--success)';
        } else {
            document.getElementById('netIncomeRow').style.background = 'var(--danger)';
        }
        
        // تحديث الميزانية العمومية
        document.getElementById('currentAssets').textContent = currentAssets.toFixed(2);
        document.getElementById('fixedAssets').textContent = fixedAssets.toFixed(2);
        document.getElementById('totalAssets').textContent = totalAssets.toFixed(2);
        
        // تحديث حقوق الملكية ليشمل صافي الربح
        const updatedEquity = totalEquity + netIncome;
        document.getElementById('totalLiabilities').textContent = totalLiabilities.toFixed(2);
        document.getElementById('totalEquity').textContent = updatedEquity.toFixed(2);
        document.getElementById('totalLiabilitiesEquity').textContent = (totalLiabilities + updatedEquity).toFixed(2);
        
        // تحديث قائمة التدفقات النقدية (مبسطة)
        document.getElementById('beginningCash').textContent = '0.00'; // يمكن تعديله لاحقاً
        document.getElementById('endingCash').textContent = cashBalance.toFixed(2);
        
        // تدفقات تشغيلية مبسطة
        const operatingCashFlow = netIncome * 0.8; // افتراض 80% من صافي الدخل كتدفق نقدي
        const investingCashFlow = -fixedAssets * 0.1; // افتراض شراء أصول
        const financingCashFlow = totalLiabilities * 0.1; // افتراض قروض
        
        document.getElementById('operatingCashFlow').textContent = operatingCashFlow.toFixed(2);
        document.getElementById('investingCashFlow').textContent = investingCashFlow.toFixed(2);
        document.getElementById('financingCashFlow').textContent = financingCashFlow.toFixed(2);
        
        const netCashFlow = operatingCashFlow + investingCashFlow + financingCashFlow;
        document.getElementById('netCashFlow').textContent = netCashFlow.toFixed(2);
    }

    // ============ إقفال الحسابات ============
    function updateClosingStats() {
        const accountBalances = {};
        
        // حساب أرصدة الحسابات (قبل الإقفال)
        allEntries.forEach(entry => {
            entry.items.forEach(item => {
                if (!accountBalances[item.accountId]) {
                    accountBalances[item.accountId] = {
                        name: item.accountName,
                        type: item.accountType,
                        debit: 0,
                        credit: 0
                    };
                }
                
                accountBalances[item.accountId].debit += item.debit;
                accountBalances[item.accountId].credit += item.credit;
            });
        });
        
        let totalRevenue = 0;
        let totalExpenses = 0;
        
        Object.values(accountBalances).forEach(acc => {
            const balance = acc.debit - acc.credit;
            
            if (acc.type === 'revenue') {
                totalRevenue += Math.abs(balance);
            } else if (acc.type === 'expense') {
                totalExpenses += Math.abs(balance);
            }
        });
        
        const netIncome = totalRevenue - totalExpenses;
        
        document.getElementById('closingRevenue').textContent = totalRevenue.toFixed(2);
        document.getElementById('closingExpenses').textContent = totalExpenses.toFixed(2);
        document.getElementById('closingNet').textContent = netIncome.toFixed(2);
        
        // تلوين صافي الدخل
        const netElement = document.getElementById('closingNet');
        if (netIncome >= 0) {
            netElement.style.color = 'var(--success)';
        } else {
            netElement.style.color = 'var(--danger)';
        }
    }

    function performClosing() {
        const accountBalances = {};
        
        // حساب أرصدة الحسابات (قبل الإقفال)
        allEntries.forEach(entry => {
            entry.items.forEach(item => {
                if (!accountBalances[item.accountId]) {
                    accountBalances[item.accountId] = {
                        id: item.accountId,
                        name: item.accountName,
                        type: item.accountType,
                        debit: 0,
                        credit: 0,
                        balance: 0
                    };
                }
                
                accountBalances[item.accountId].debit += item.debit;
                accountBalances[item.accountId].credit += item.credit;
                accountBalances[item.accountId].balance = accountBalances[item.accountId].debit - accountBalances[item.accountId].credit;
            });
        });
        
        // إيجاد حساب الأرباح المحتجزة
        const retainedEarnings = accounts.find(acc => acc.name === "أرباح محتجزة");
        if (!retainedEarnings) {
            alert('يرجى إضافة حساب "أرباح محتجزة" أولاً');
            return;
        }
        
        // حساب صافي الربح/الخسارة
        let totalRevenue = 0;
        let totalExpenses = 0;
        let closingEntriesToAdd = [];
        
        Object.values(accountBalances).forEach(acc => {
            if (acc.type === 'revenue' && Math.abs(acc.balance) > 0.01) {
                // إقفال حساب الإيرادات
                const closingEntry = {
                    id: Date.now() + Math.random(),
                    date: new Date().toLocaleDateString('ar-IQ'),
                    time: new Date().toLocaleTimeString('ar-IQ'),
                    description: `إقفال حساب ${acc.name}`,
                    items: [],
                    closing: true
                };
                
                if (acc.balance > 0) {
                    // حساب الإيرادات له رصيد دائن
                    closingEntry.items.push({
                        accountId: acc.id,
                        accountName: acc.name,
                        accountType: acc.type,
                        debit: Math.abs(acc.balance),
                        credit: 0
                    });
                    
                    closingEntry.items.push({
                        accountId: retainedEarnings.id,
                        accountName: retainedEarnings.name,
                        accountType: retainedEarnings.type,
                        debit: 0,
                        credit: Math.abs(acc.balance)
                    });
                }
                
                totalRevenue += Math.abs(acc.balance);
                if (closingEntry.items.length > 0) {
                    closingEntriesToAdd.push(closingEntry);
                }
            }
            
            if (acc.type === 'expense' && Math.abs(acc.balance) > 0.01) {
                // إقفال حساب المصاريف
                const closingEntry = {
                    id: Date.now() + Math.random(),
                    date: new Date().toLocaleDateString('ar-IQ'),
                    time: new Date().toLocaleTimeString('ar-IQ'),
                    description: `إقفال حساب ${acc.name}`,
                    items: [],
                    closing: true
                };
                
                if (acc.balance > 0) {
                    // حساب المصاريف له رصيد مدين
                    closingEntry.items.push({
                        accountId: retainedEarnings.id,
                        accountName: retainedEarnings.name,
                        accountType: retainedEarnings.type,
                        debit: Math.abs(acc.balance),
                        credit: 0
                    });
                    
                    closingEntry.items.push({
                        accountId: acc.id,
                        accountName: acc.name,
                        accountType: acc.type,
                        debit: 0,
                        credit: Math.abs(acc.balance)
                    });
                }
                
                totalExpenses += Math.abs(acc.balance);
                if (closingEntry.items.length > 0) {
                    closingEntriesToAdd.push(closingEntry);
                }
            }
        });
        
        const netIncome = totalRevenue - totalExpenses;
        
        // حفظ قيود الإقفال
        closingEntries = closingEntriesToAdd;
        localStorage.setItem('closing_entries', JSON.stringify(closingEntries));
        
        // تحديث الواجهة
        const resultsDiv = document.getElementById('closingResults');
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>تم إقفال الحسابات بنجاح!</strong><br>
                • إجمالي الإيرادات: ${totalRevenue.toFixed(2)}<br>
                • إجمالي المصاريف: ${totalExpenses.toFixed(2)}<br>
                • صافي الربح/الخسارة: ${netIncome.toFixed(2)}<br>
                • تم إضافة ${closingEntries.length} قيود إقفال
            </div>
        `;
        
        // تحديث جميع التقارير
        renderJournal();
        renderLedger();
        renderTrialBalance();
        generateFinancialStatements();
        updateClosingStats();
    }

    function closeTemporaryAccounts() {
        showTab('closing');
    }

    // ============ وظائف مساعدة ============
    function saveAccounts() {
        localStorage.setItem('accounting_accounts', JSON.stringify(accounts));
    }

    function saveEntries() {
        localStorage.setItem('accounting_entries', JSON.stringify(allEntries));
    }

    function showMessage(message, type) {
        const messageDiv = document.getElementById('entryMessage');
        messageDiv.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        
        setTimeout(() => {
            messageDiv.innerHTML = '';
        }, 5000);
    }

    function showStats() {
        document.getElementById('statEntries').textContent = allEntries.length;
        document.getElementById('statAccounts').textContent = accounts.length;
        
        let totalDebit = 0;
        let totalCredit = 0;
        
        allEntries.forEach(entry => {
            entry.items.forEach(item => {
                totalDebit += item.debit;
                totalCredit += item.credit;
            });
        });
        
        document.getElementById('statTotalDebit').textContent = totalDebit.toFixed(2);
        document.getElementById('statTotalCredit').textContent = totalCredit.toFixed(2);
        
        document.getElementById('statsModal').style.display = 'flex';
    }

    function closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    function exportData() {
        const data = {
            accounts: accounts,
            entries: allEntries,
            closingEntries: closingEntries,
            exportDate: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        const link = document.createElement('a');
        link.setAttribute('href', dataUri);
        link.setAttribute('download', 'accounting_data_' + new Date().toISOString().split('T')[0] + '.json');
        link.click();
    }

    function exportFinancialStatements() {
        generateFinancialStatements();
        
        const statements = {
            incomeStatement: {
                revenue: document.getElementById('totalRevenue').textContent,
                expenses: document.getElementById('totalExpenses').textContent,
                netIncome: document.getElementById('netIncome').textContent
            },
            balanceSheet: {
                assets: document.getElementById('totalAssets').textContent,
                liabilities: document.getElementById('totalLiabilities').textContent,
                equity: document.getElementById('totalEquity').textContent
            },
            cashFlow: {
                netCashFlow: document.getElementById('netCashFlow').textContent,
                endingCash: document.getElementById('endingCash').textContent
            },
            exportDate: new Date().toLocaleString('ar-IQ')
        };
        
        let text = `القوائم المالية\n`;
        text += `================\n\n`;
        text += `قائمة الدخل:\n`;
        text += `  الإيرادات: ${statements.incomeStatement.revenue}\n`;
        text += `  المصاريف: ${statements.incomeStatement.expenses}\n`;
        text += `  صافي الربح/الخسارة: ${statements.incomeStatement.netIncome}\n\n`;
        text += `الميزانية العمومية:\n`;
        text += `  الموجودات: ${statements.balanceSheet.assets}\n`;
        text += `  المطلوبات: ${statements.balanceSheet.liabilities}\n`;
        text += `  حقوق الملكية: ${statements.balanceSheet.equity}\n\n`;
        text += `قائمة التدفقات النقدية:\n`;
        text += `  صافي التدفق النقدي: ${statements.cashFlow.netCashFlow}\n`;
        text += `  الرصيد النقدي النهائي: ${statements.cashFlow.endingCash}\n\n`;
        text += `تاريخ التصدير: ${statements.exportDate}`;
        
        const dataUri = 'data:text/plain;charset=utf-8,'+ encodeURIComponent(text);
        const link = document.createElement('a');
        link.setAttribute('href', dataUri);
        link.setAttribute('download', 'financial_statements_' + new Date().toISOString().split('T')[0] + '.txt');
        link.click();
    }

    function resetAllData() {
        if (confirm('⚠️ تحذير: سيتم حذف جميع البيانات بما في ذلك الحسابات والقيود. هل أنت متأكد؟')) {
            localStorage.clear();
            accounts = [
                { id: 1, name: "نقدية بالصندوق", type: "asset" },
                { id: 2, name: "بنك", type: "asset" },
                { id: 3, name: "مدينون", type: "asset" },
                { id: 4, name: "مخزون", type: "asset" },
                { id: 5, name: "أثاث ومعدات", type: "asset" },
                { id: 6, name: "مباني", type: "asset" },
                { id: 7, name: "دائنون", type: "liability" },
                { id: 8, name: "قروض", type: "liability" },
                { id: 9, name: "رأس المال", type: "equity" },
                { id: 10, name: "أرباح محتجزة", type: "equity" },
                { id: 11, name: "مبيعات", type: "revenue" },
                { id: 12, name: "إيرادات خدمات", type: "revenue" },
                { id: 13, name: "مشتريات", type: "expense" },
                { id: 14, name: "رواتب وأجور", type: "expense" },
                { id: 15, name: "إيجار", type: "expense" },
                { id: 16, name: "كهرباء وماء", type: "expense" },
                { id: 17, name: "صيانة", type: "expense" },
                { id: 18, name: "مصاريف تسويق", type: "expense" },
                { id: 19, name: "مصاريف إدارية", type: "expense" },
                { id: 20, name: "مصاريف إهلاك", type: "expense" }
            ];
            allEntries = [];
            closingEntries = [];
            saveAccounts();
            saveEntries();
            updateAccountSelect();
            clearEntryForm();
            renderJournal();
            renderLedger();
            renderTrialBalance();
            renderAccountsList();
            generateFinancialStatements();
            
            showMessage('تم تصفير جميع البيانات بنجاح', 'success');
        }
    }

    function clearAccountForm() {
        document.getElementById('newAccountName').value = '';
        document.getElementById('newAccountType').value = '';
    }
</script>
</body>
</html>
