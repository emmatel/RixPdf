from telegram import Update, InputFile, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
import io
import arabic_reshaper
from bidi.algorithm import get_display
import os
import json
from telegram import Update
from telegram.ext import CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import os
import json
import io
import re
import os
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
import glob


TOKEN = '7150624571:AAExh0HuYTi-8L9iGEYALWVju-I6R2gH_vc'  # استبدل بتوكن البوت الخاص بك
collected_messages = []  # قائمة لتجميع الرسائل
allowed_users = [288502493]  # قائمة المستخدمين المسموح لهم بالوصول
file_name = ""  # اسم الملف المطلوب
saved_files = {}  # قاموس لتخزين الملفات والرسائل المحفوظة
file_creation_in_progress = False  # متغير لتتبع عملية إنشاء الملف
store_directory = "Store"  # مجلد لتخزين الملفات

def load_data():
    global allowed_users, saved_files
    try:
        with open("allowed_users.json", "r") as f:
            allowed_users = json.load(f)
    except FileNotFoundError:
        allowed_users = [288502493]  # استبدل 288502493 بمعرف المستخدم الخاص بك

    try:
        with open("saved_files.json", "r") as f:
            saved_files = json.load(f)
    except FileNotFoundError:
        saved_files = {}




#import logging
#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')





# Register a TrueType font (supports Arabic)
pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))

def check_user(update: Update, context: CallbackContext) -> bool:
    user_id = update.message.from_user.id
    return user_id in allowed_users


def start(update: Update, context: CallbackContext) -> None:
    if not check_user(update, context):
        update.message.reply_text("عذراً، ليس لديك الإذن لاستخدام هذا البوت، تواصل مع مالك البوت إذا احتجت مساعدة T.me/RixRixes.")
        return

    keyboard = [
        ["إنشاء WORD", "إنشاء PDF"],
        ["عرض المحفوظات Word", "عرض المحفوظات PDF"],
        ["حذف ملف Word", "حذف ملف PDF"],
        ["حذف كل ملفات Word", "حذف كل ملفات PDF"],
        ["تجميع الرسائل"],
        ["إلغاء تجميع الرسائل"],
        ["إزالة ID مستخدم", "إضافة ID مستخدم"],
        ["حظر كل المستخدمين", "عرض ID المستخدمين"],
        ["إذاعة رسالة"],
        ["بدء / إعادة تشغيل البوت"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_text(
        "أرسل الرسائل التي تريد دمجها، ثم استخدم الأوامر المناسبة.",
        reply_markup=reply_markup
    )





def collect_message(update: Update, context: CallbackContext) -> None:
    """
    جمع الرسائل المرسلة من المستخدم.
    """
    if not check_user(update, context):
        return

    collected_messages.append(update.message.text)




global file_format

def create_pdf(update, context):
    global file_name, file_format, last_file_format, last_messages

    file_format = "pdf"
    last_file_format = file_format
    last_messages = collected_messages.copy()

    """
    إنشاء ملف PDF من الرسائل المجمعة.
    """
    if not check_user(update, context):
        return

    file_name, file_format

    file_format = "pdf"

    # استخدم محتوى قبل آخر رسالة كاسم لملف PDF
    if len(collected_messages) >= 2:
        file_name = f"{collected_messages[-1].strip()}"
    else:
        file_name = f"ملف PDF-{update.message.from_user.id}"

    # ... (الكود المتبقي لإنشاء PDF)

    pdf_io = io.BytesIO()
    c = canvas.Canvas(pdf_io)
    c.setFont('Arabic', 14)  # Set the font to the registered Arabic font
    text_object = c.beginText(72, 800)
    for message in collected_messages[:-1]:  # تجاهل الرسالة الأخيرة
        reshaped_text = arabic_reshaper.reshape(message)  # Reshape the text
        bidi_text = get_display(reshaped_text)  # Apply right-to-left
        text_object.textLine(bidi_text)
        text_object.textLine("")  # سطر فارغ بين الرسائل

    c.drawText(text_object)
    c.save()

    file_path = save_file(pdf_io, file_name, "pdf")
    save_data(file_name, "pdf")  # استدعاء الدالة save_data مع اثنين من الوسائط فقط

    pdf_io.seek(0)
    update.message.reply_document(document=InputFile(pdf_io, f"{file_name}.pdf"), filename=f"{file_name}.pdf")

    collected_messages.clear()

    ask_to_save_file(update, context, "pdf")  # يسأل المستخدم إذا كان يريد حفظ الملف



def create_word(update, context):
    global file_name, file_format, last_file_format, last_messages

    file_format = "docx"
    last_file_format = file_format
    last_messages = collected_messages.copy()

    """
    إنشاء ملف WORD من الرسائل المجمعة.
    """
    if not check_user(update, context):
        return

    file_name, file_format

    file_format = "docx"

    # استخدم محتوى قبل آخر رسالة كاسم لملف WORD
    if len(collected_messages) >= 2:
        file_name = f"{collected_messages[-1].strip()}"
    else:
        file_name = f"ملف WORD-{update.message.from_user.id}"

    # ... (الكود المتبقي لإنشاء Word)

    doc = Document()
    for message in collected_messages[:-1]:  # تجاهل الرسالة الأخيرة
        reshaped_text = arabic_reshaper.reshape(message)  # Reshape the text
        bidi_text = get_display(reshaped_text)  # Apply right-to-left
        doc.add_paragraph(bidi_text)

    doc_io = io.BytesIO()
    doc.save(doc_io)

    file_path = save_file(doc_io, file_name, "docx")
    save_data(file_name, "docx")  # استدعاء الدالة save_data مع اثنين من الوسائط فقط

    doc_io.seek(0)
    update.message.reply_document(document=InputFile(doc_io, f"{file_name}.docx"), filename=f"{file_name}.docx")

    collected_messages.clear()

    ask_to_save_file(update, context, "docx")  # يسأل المستخدم إذا كان يريد حفظ الملف






def ask_to_save_file(update: Update, context: CallbackContext, file_format: str) -> None:
    """
    يسأل المستخدم إذا كان يريد حفظ الملف.
    """
    keyboard = [["لا", "نعم"]]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_text(
        "هل تريد حفظ الملف؟",
        reply_markup=reply_markup
    )




def yes(update: Update, context: CallbackContext) -> None:
    """
    يتعامل مع الرسالة "نعم".
    """
    if not check_user(update, context):
        return

    if update.message.text == "نعم":
        update.message.reply_text(
            "تم حفظ الملف بنجاح. يمكنك الآن إرسال طلبات جديدة.",
        )

        # إضافة الأزرار الجديدة بعد الرد بـ "نعم"
        keyboard = [["العودة", "إنشاء ملف من الصيغة الثانية"]]
        reply_markup = ReplyKeyboardMarkup(keyboard)

        update.message.reply_text(
            "هل تريد القيام بشيء آخر؟",
            reply_markup=reply_markup
        )

def golden_button(update, context):
    global collected_messages

    # استخدم نفس الرسائل التي تم استخدامها في إنشاء الملف pdf أو word الأخير
    collected_messages = last_messages.copy()

    if last_file_format == "docx":
        create_pdf(update, context)
    else:
        create_word(update, context)

    update.message.reply_text(
        "تم إنشاء الملف بنجاح. يمكنك الآن إرسال طلبات جديدة.",
    )
    start(update, context)  # استدعاء الدالة start مرة أخرى


def back(update: Update, context: CallbackContext) -> None:
    """
    يتعامل مع الرسالة "العودة".
    """
    if not check_user(update, context):
        return

    if update.message.text == "العودة":
        update.message.reply_text(
            "عودة",
        )
        start(update, context)  # إعادة استدعاء الدالة start


def no(update: Update, context: CallbackContext) -> None:
    """
    يتعامل مع الرسالة "لا".
    """
    if not check_user(update, context):
        return

    if update.message.text == "لا":
        # تحقق من نوع الملف واستخدم الاسم المناسب لملف JSON
        if file_format == "docx":
            data_file = "saved_word.json"
        else:
            data_file = f"saved_{file_format}.json"

        file_path = os.path.join(os.getcwd(), "PDF files" if file_format == "pdf" else "Word files",
                                 f"{file_name}.{file_format}")
        if os.path.exists(file_path):
            os.remove(file_path)

        # حذف اسم الملف من ملف json
        if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
            with open(data_file, "r") as f:
                data = json.load(f)
            if file_name in data:
                del data[file_name]
            with open(data_file, "w") as f:
                json.dump(data, f)

        update.message.reply_text(
            "تم حذف الملف بنجاح. يمكنك الآن إرسال طلبات جديدة.",
        )
        start(update, context)  # إعادة استدعاء الدالة start


import os
import shutil

def save_file(file_io, file_name, file_format):
    """
    حفظ الملف على القرص وإرجاع مسار الملف.
    """
    directory = "PDF files" if file_format == "pdf" else "Word files"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(os.getcwd(), directory, f"{file_name}.{file_format}")
    with open(file_path, "wb") as f:
        f.write(file_io.getvalue())
    return file_path



def save_data(file_name, file_format):
    """
    حفظ اسم الملف في ملف JSON.
    """
    # تحقق من نوع الملف واستخدم الاسم المناسب لملف JSON
    if file_format == "docx":
        data_file = "saved_word.json"
    else:
        data_file = f"saved_{file_format}.json"

    data = {}
    if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
        with open(data_file, "r") as f:
            data = json.load(f)

    data[file_name] = file_name  # حفظ اسم الملف فقط

    with open(data_file, "w") as f:
        json.dump(data, f)


def show_saved_pdf(update: Update, context: CallbackContext) -> None:
    """
    عرض الملفات المحفوظة من نوع PDF.
    """
    if not check_user(update, context):
        return

    try:
        with open("saved_pdf.json", "r") as f:
            saved_files = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        update.message.reply_text("قائمة محفوظات الملفات PDF فارغة.")
        return

    if not saved_files:
        update.message.reply_text("قائمة محفوظات الملفات PDF فارغة.")
        return

    # إرسال قائمة بأسماء الملفات المحفوظة
    update.message.reply_text("\n".join(saved_files.keys()))

def show_saved_word(update: Update, context: CallbackContext) -> None:
    """
    عرض الملفات المحفوظة من نوع Word.
    """
    if not check_user(update, context):
        return

    try:
        with open("saved_word.json", "r") as f:
            saved_files = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        update.message.reply_text("قائمة محفوظات الملفات Word فارغة.")
        return

    if not saved_files:
        update.message.reply_text("قائمة محفوظات الملفات Word فارغة.")
        return

    # إرسال قائمة بأسماء الملفات المحفوظة
    update.message.reply_text("\n".join(saved_files.keys()))




import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

def load_allowed_users():
    # فتح ملف JSON
    with open('allowed_users.json', 'r') as f:
        # تحميل بيانات JSON
        data = json.load(f)
    # إرجاع البيانات
    return data

# الآن يمكنك استخدام الدالة في الكود الخاص بك
allowed_user_ids = load_allowed_users()

def broadcast_option(update: Update, context: CallbackContext) -> None:
    # تخزين الرسالة الأخيرة في السياق لاستخدامها لاحقًا
    context.user_data['broadcast_message'] = update.message.text

    # إنشاء زر الإذاعة على الكيبورد
    keyboard_broadcast = [['إذاعة'], ['عودة']]
    reply_markup_broadcast = ReplyKeyboardMarkup(keyboard_broadcast, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text(
        "اكتب رسالتك ثم انقر على 'إذاعة' لنشرها أو 'العودة' للرجوع.",
        reply_markup=reply_markup_broadcast
    )

def collect_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text
    if 'collected_messages' not in context.user_data:
        context.user_data['collected_messages'] = [message_text]
    else:
        context.user_data['collected_messages'].append(message_text)

def broadcast(update: Update, context: CallbackContext) -> None:
    # التحقق أن القائمة تحتوي على رسالتين على الأقل لاختيار الرسالة السابقة للأخيرة
    if 'collected_messages' in context.user_data and len(context.user_data['collected_messages']) >= 1:
        # استرجاع الرسالة التي قبل الأخيرة
        broadcast_message = context.user_data['collected_messages'][-1].strip()

        # لا حاجة للخط الثاني في الكود الأصلي لأننا نتعامل مع قائمة مجموعة الرسائل مباشرة.

        # البدء بعملية الإذاعة
        for user_id in allowed_user_ids:
            try:
                context.bot.send_message(chat_id=user_id, text=broadcast_message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")

        update.message.reply_text("تم إذاعة رسالتك بنجاح!")
        # بعد إذاعة الرسالة، ننظف الرسالة من القائمة إذا رغبنا بذلك.
        # context.user_data['collected_messages'].pop(-2)
        start(update, context)

    else:
        # في حال لم تكن هناك رسائل كافية للإذاعة
        update.message.reply_text("لا توجد رسائل كافية للإذاعة.")
        start(update, context)


def go_back(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('عودة', reply_markup=ReplyKeyboardRemove())
    start(update, context)


















# ضع بقية الكود هنا، مثل تعريف معالج الرسائل وتفعيله


def delete_all_pdf(update: Update, context: CallbackContext):
    keyboard = [["كلا، لا تحذف", "نعم، احذف"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('هل أنت متأكيد أنك تريد حذف جميع ملفات PDF؟', reply_markup=reply_markup)


def handle_confirmed_pdf(update: Update, context: CallbackContext):
    if update.message.text == "بالتأكيد":
        # إسم الملف حيث تُحفظ معلومات وثائق PDF المُحفوظة.
        data_file = "saved_pdf.json"

        # رسالة البدء
        update.message.reply_text('يتم الآن حذف الملفات...')

        # حذف جميع الملفات من مجلد "PDF files"
        files = glob.glob('PDF files/*.pdf')
        for f in files:
            os.remove(f)

        # تحقق من وجود الملف وحجمه
        if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
            with open(data_file, "r+") as f:
                # إفراغ الـ JSON بعد حذف الملفات
                files = {}
                # إعادة وضع ملف JSON خالي
                f.seek(0)
                f.truncate()
                json.dump(files, f)
            # إعلام المستخدم بالنجاح
            update.message.reply_text('تم حذف جميع الملفات بنجاح.')
            start(update, context)
        else:
            update.message.reply_text('لا يوجد أي ملفات محفوظة حالياً.')
            start(update, context)


def handle_not_confirmed_pdf(update: Update, context: CallbackContext):
    update.message.reply_text('تم إلغاء عملية الحذف.')
    # إعادة تنفيذ الأمر /start
    start(update, context)






# قائمة المستخدمين المسموح لهم
allowed_users = []

def ban_all_users(update: Update, context: CallbackContext):
    keyboard = [["لا، قم بالتراجع", "نعم احظر الكل"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('هل أنت متأكيد أنك تريد حظر جميع المستخدمين؟', reply_markup=reply_markup)

def save_users_to_file():
    """
    حفظ قائمة المستخدمين المسموح لهم إلى ملف JSON.
    """
    data_file = "allowed_users.json"
    with open(data_file, "w") as f:
        json.dump(allowed_users, f)

def handle_confirmed_ban(update: Update, context: CallbackContext):
    # رسالة البدء
    update.message.reply_text('يتم الآن حظر المستخدمين...')

    # حظر كل المستخدمين المُدرجة في هذا الـ JSON باستثناء المستخدم الأصلي
    global allowed_users
    allowed_users = [user for user in allowed_users if user == 288502493]

    # حفظ القائمة إلى الملف
    save_users_to_file()

    # إعلام المستخدم بالنجاح
    update.message.reply_text('تم حظر جميع المستخدمين بنجاح.')
    start(update, context)

def handle_not_confirmed_ban(update: Update, context: CallbackContext):
    update.message.reply_text('تم إلغاء عملية الحظر.')
    # إعادة تنفيذ الأمر /start
    start(update, context)







def delete_all_word(update: Update, context: CallbackContext):
    keyboard = [["كلا", "بالتأكيد"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('هل أنت متأكيد أنك تريد حذف جميع ملفات Word؟', reply_markup=reply_markup)


def handle_confirmed_word(update: Update, context: CallbackContext):
    if update.message.text == "بالتأكيد":
        # إسم الملف حيث تُحفظ معلومات وثائق Word المُحفوظة.
        data_file = "saved_word.json"

        # رسالة البدء
        update.message.reply_text('يتم الآن حذف الملفات...')

        # حذف جميع الملفات من مجلد "Word files"
        files = glob.glob('Word files/*.docx')
        for f in files:
            os.remove(f)

        # تحقق من وجود الملف وحجمه
        if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
            with open(data_file, "r+") as f:
                # إفراغ الـ JSON بعد حذف الملفات
                files = {}
                # إعادة وضع ملف JSON خالي
                f.seek(0)
                f.truncate()
                json.dump(files, f)
            # إعلام المستخدم بالنجاح
            update.message.reply_text('تم حذف جميع الملفات بنجاح.')
            start(update, context)
        else:
            update.message.reply_text('لا يوجد أي ملفات محفوظة حالياً.')
            start(update, context)


def handle_not_confirmed_word(update: Update, context: CallbackContext):
    update.message.reply_text('تم إلغاء عملية الحذف.')
    # إعادة تنفيذ الأمر /start
    start(update, context)








def send_combined(update: Update, context: CallbackContext) -> None:
    """
    إرسال الرسائل المجمعة في رسالة واحدة.
    """
    if not check_user(update, context):
        return

    if not collected_messages:
        update.message.reply_text("لم ترسل أي رسائل لإعادة إرسالها.")
        return

    combined_message = "\n".join(collected_messages)  # تجميع الرسائل مع سطر فارغ بينهم
    update.message.reply_text(combined_message)

    saved_files["combined_message"] = combined_message  # حفظ الرسائل في التخزين
    collected_messages.clear()
    save_data()

def cancel_collect(update: Update, context: CallbackContext) -> None:
    """
    إلغاء تجميع الرسائل المجمعة.
    """
    if not check_user(update, context):
        return

    if not collected_messages:
        update.message.reply_text("لم ترسل أي رسائل لإلغاء تجميعها.")
        return

    for message in collected_messages:
        lines = message.split('\n')
        for line in lines:
            update.message.reply_text(line)

    collected_messages.clear()




collected_messages = []

# تعريف ID المستخدم الأصلي
original_user_id = 288502493

def handle_message(update: Update, context: CallbackContext) -> None:
    global collected_messages
    # تحديث الرسائل المجمعة في كل مرة يتم فيها استلام رسالة جديدة
    collected_messages.append(update.message.text)





def add_user(update: Update, context: CallbackContext) -> None:
    global collected_messages
    # فقط المستخدم الأصلي يمكنه إضافة مستخدمين
    if update.message.from_user.id != original_user_id:
        return

    if len(collected_messages) >= 1:
        user_id = int(collected_messages[-1])
        with open("allowed_users.json", "r") as f:
            allowed_users = json.load(f)
        allowed_users.append(user_id)
        with open("allowed_users.json", "w") as f:
            json.dump(allowed_users, f)
        update.message.reply_text(f"تمت إضافة المستخدم {user_id}.")
    else:
        update.message.reply_text("لم يتم توفير ID المستخدم.")

def remove_user(update: Update, context: CallbackContext) -> None:
    global collected_messages
    # فقط المستخدم الأصلي يمكنه إزالة مستخدمين
    if update.message.from_user.id != original_user_id:
        return

    if len(collected_messages) >= 1:
        user_id = int(collected_messages[-1])
        # لا يمكن إزالة المستخدم الأصلي
        if user_id == original_user_id:
            update.message.reply_text("لا يمكن إزالة المستخدم الأصلي.")
            return
        with open("allowed_users.json", "r") as f:
            allowed_users = json.load(f)
        if user_id in allowed_users:
            allowed_users.remove(user_id)
            with open("allowed_users.json", "w") as f:
                json.dump(allowed_users, f)
            update.message.reply_text(f"تمت إزالة المستخدم {user_id}.")
        else:
            update.message.reply_text(f"المستخدم {user_id} غير موجود في القائمة.")
    else:
        update.message.reply_text("لم يتم توفير ID المستخدم.")





def load_users_from_file():
    """
    تحميل قائمة المستخدمين المسموح لهم من ملف JSON.
    """
    data_file = "allowed_users.json"
    if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
        with open(data_file, "r") as f:
            return json.load(f)
    else:
        return []

# قائمة المستخدمين المسموح لهم
allowed_users = load_users_from_file()

def show_users(update: Update, context: CallbackContext) -> None:
    """
    عرض قائمة المستخدمين المسموح لهم بالوصول إلى البوت.
    """
    if not check_user(update, context):
        return

    # تحديث القائمة من الملف
    global allowed_users
    allowed_users = load_users_from_file()

    if not allowed_users:
        update.message.reply_text("لم يتم إضافة أي مستخدمين.")
        return

    for user_id in allowed_users:
        update.message.reply_text(str(user_id))


def confirm_delete_pdf(update: Update, context: CallbackContext) -> None:
    """
    يتعامل مع الرسالة "حذف ملف PDF".
    """
    if not check_user(update, context):
        return

    if update.message.text == "حذف ملف PDF":
        keyboard = [["لا، لا تقم بحذفه", "نعم احذف ملف ال PDF"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('هل أنت متأكد أنك تريد حذف ملف PDF؟', reply_markup=reply_markup)

def delete_pdf(update: Update, context: CallbackContext) -> None:
    """
    يتعامل مع الرسالة "نعم احذف ملف ال PDF".
    """
    if not check_user(update, context):
        return

    if update.message.text.startswith("نعم احذف ملف ال PDF"):
        # اقرأ اسم الملف من الرسالة قبل الأخيرة إذا كانت موجودة
        if len(collected_messages) >= 1:
            file_name = collected_messages[-1].split(" ")[-1]
        else:
            update.message.reply_text(
                "عذرًا، لا يمكنني العثور على اسم الملف. يرجى المحاولة مرة أخرى."
            )
            return

        # حذف الملف من القرص
        file_path = os.path.join(os.getcwd(), "PDF files", f"{file_name}.pdf")
        if os.path.exists(file_path):
            os.remove(file_path)

        # حذف اسم الملف ومساره من ملف json
        data_file = "saved_pdf.json"
        if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
            with open(data_file, "r") as f:
                data = json.load(f)
            if file_name in data:
                del data[file_name]
            with open(data_file, "w") as f:
                json.dump(data, f)

        update.message.reply_text(
            f"تم حذف الملف {file_name} بنجاح. يمكنك الآن إرسال طلبات جديدة.",
        )
        start(update, context)  # إعادة استدعاء الدالة start


def handle_not_confirmed_delete_pdf(update: Update, context: CallbackContext) -> None:
    if update.message.text == "لا، لا تقم بحذفه":
        update.message.reply_text('تم إلغاء عملية الحذف.')
        start(update, context)  # إعادة استدعاء الدالة start







def confirm_delete_word(update: Update, context: CallbackContext) -> None:
    """
    يتعامل مع الرسالة "حذف ملف Word".
    """
    if not check_user(update, context):
        return

    if update.message.text == "حذف ملف Word":
        keyboard = [["لا تقم بحذفه", "نعم احذف ملف ال Word"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('هل أنت متأكد أنك تريد حذف ملف Word؟', reply_markup=reply_markup)

def delete_word(update: Update, context: CallbackContext) -> None:
    """
    يتعامل مع الرسالة "نعم احذف ملف ال Word".
    """
    if not check_user(update, context):
        return

    if update.message.text.startswith("نعم احذف ملف ال Word"):
        # اقرأ اسم الملف من الرسالة قبل الأخيرة إذا كانت موجودة
        if len(collected_messages) >= 1:
            file_name = collected_messages[-1].split(" ")[-1]
        else:
            update.message.reply_text(
                "عذرًا، لا يمكنني العثور على اسم الملف. يرجى المحاولة مرة أخرى."
            )
            return

        # حذف الملف من القرص
        file_path = os.path.join(os.getcwd(), "Word files", f"{file_name}.docx")
        if os.path.exists(file_path):
            os.remove(file_path)

        # حذف اسم الملف ومساره من ملف json
        data_file = "saved_word.json"
        if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
            with open(data_file, "r") as f:
                data = json.load(f)
            if file_name in data:
                del data[file_name]
            with open(data_file, "w") as f:
                json.dump(data, f)

        update.message.reply_text(
            f"تم حذف الملف {file_name}. بنجاح. يمكنك الآن إرسال طلبات جديدة.",
        )
        start(update, context)  # إعادة استدعاء الدالة start



def handle_not_confirmed_delete_word(update: Update, context: CallbackContext) -> None:
    if update.message.text == "لا، لا تقم بحذفه":
        update.message.reply_text('تم إلغاء عملية الحذف.')
        start(update, context)  # إعادة استدعاء الدالة start








def help_command(update: Update, context: CallbackContext) -> None:
    """
    عرض معلومات حول استخدام البوت.
    """
    update.message.reply_text(
        """
        **أوامر البوت:**

        /start: بدء استخدام البوت.
        /help: عرض معلومات حول استخدام البوت.
        /إنشاء PDF: إنشاء ملف PDF من الرسائل المجمعة.
        /إنشاء WORD: إنشاء ملف WORD من الرسائل المجمعة.
        /تجميع الرسائل: تجميع الرسائل المرسلة في رسالة واحدة.
        /إلغاء تجميع الرسائل: إلغاء تجميع الرسائل المجمعة.
        /حفظ: حفظ الرسائل أو الملفات المجمعة.
        /عرض المحفوظات: عرض الرسائل أو الملفات المحفوظة.
        /عرض المستخدمين: عرض قائمة المستخدمين المسموح لهم بالوصول إلى البوت.
        /إضافة مستخدم: إضافة مستخدم جديد إلى قائمة المستخدمين المسموح لهم بالوصول إلى البوت.
        /إزالة مستخدم: إزالة مستخدم من قائمة المستخدمين المسموح لهم بالوصول إلى البوت.
        """,
        reply_markup=ReplyKeyboardRemove()
    )



def main() -> None:
    """
    نقطة الدخول الرئيسية للبوت.
    """
    load_data()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # إضافة معالجة الأوامر
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler('delete_all_pdf', delete_all_pdf))
    dp.add_handler(CommandHandler('delete_all_word', delete_all_word))
    dp.add_handler(CommandHandler('handle_not_confirmed_word', handle_not_confirmed_word))

    # إضافة معالجة الرسائل النصية
    dp.add_handler(MessageHandler(Filters.regex('^إنشاء PDF$'), create_pdf))
    dp.add_handler(MessageHandler(Filters.regex('^إنشاء WORD$'), create_word))
    dp.add_handler(MessageHandler(Filters.regex('^تجميع الرسائل$'), send_combined))
    dp.add_handler(MessageHandler(Filters.regex('^إلغاء تجميع الرسائل$'), cancel_collect))
    dp.add_handler(MessageHandler(Filters.regex('^عرض المحفوظات PDF$'), show_saved_pdf))
    dp.add_handler(MessageHandler(Filters.regex('^عرض المحفوظات Word$'), show_saved_word))
    dp.add_handler(MessageHandler(Filters.regex('^عرض ID المستخدمين$'), show_users))
    dp.add_handler(MessageHandler(Filters.regex('^إضافة ID مستخدم$'), add_user))
    dp.add_handler(MessageHandler(Filters.regex('^إزالة ID مستخدم$'), remove_user))
    dp.add_handler(MessageHandler(Filters.regex('^حظر كل المستخدمين$'), ban_all_users))
    dp.add_handler(MessageHandler(Filters.regex('^بدء / إعادة تشغيل البوت$'), start))
    dp.add_handler(MessageHandler(Filters.regex('^نعم$'), yes))
    dp.add_handler(MessageHandler(Filters.regex('^لا$'), no))
    dp.add_handler(MessageHandler(Filters.regex('^حذف كل ملفات PDF$'), delete_all_pdf))
    dp.add_handler(MessageHandler(Filters.regex('^حذف كل ملفات Word$'), delete_all_word))
    dp.add_handler(MessageHandler(Filters.regex('^بالتأكيد$'), handle_confirmed_word))
    dp.add_handler(MessageHandler(Filters.regex('^كلا$'), handle_not_confirmed_word))
    dp.add_handler(MessageHandler(Filters.regex('^نعم، احذف$'), handle_confirmed_pdf))
    dp.add_handler(MessageHandler(Filters.regex('^كلا، لا تحذف$'), handle_not_confirmed_pdf))
    dp.add_handler(MessageHandler(Filters.regex('^نعم احظر الكل$'), handle_confirmed_ban))
    dp.add_handler(MessageHandler(Filters.regex('^لا، قم بالتراجع$'), handle_not_confirmed_ban))

    dp.add_handler(MessageHandler(Filters.regex('^حذف ملف PDF$'), confirm_delete_pdf))
    dp.add_handler(MessageHandler(Filters.regex('^نعم احذف ملف ال PDF$'), delete_pdf))
    dp.add_handler(MessageHandler(Filters.regex('^لا، لا تقم بحذفه$'), handle_not_confirmed_delete_pdf))

    dp.add_handler(MessageHandler(Filters.regex('^حذف ملف Word$'), confirm_delete_word))
    dp.add_handler(MessageHandler(Filters.regex('^نعم احذف ملف ال Word$'), delete_word))
    dp.add_handler(MessageHandler(Filters.regex('^لا تقم بحذفه$'), handle_not_confirmed_delete_word))

    dp.add_handler(MessageHandler(Filters.regex('^إنشاء ملف من الصيغة الثانية$'), golden_button))
    dp.add_handler(MessageHandler(Filters.regex('^العودة$'), back))


    dp.add_handler(MessageHandler(Filters.regex('^إذاعة رسالة$'), broadcast_option))
    dp.add_handler(MessageHandler(Filters.regex('^إذاعة$'), broadcast))
    dp.add_handler(MessageHandler(Filters.regex('^عودة$'), go_back))






    dp.add_handler(MessageHandler(Filters.text, collect_message))

    # بَدْء تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
