import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='stringMatching'
)

def add_question(question, answer):
    mycursor = mydb.cursor()
    sql = "INSERT INTO data (pertanyaan, jawaban) VALUES (%s, %s)"
    val = (question, answer)
    mycursor.execute(sql, val)
    mydb.commit()
    print("Pertanyaan dan jawaban telah ditambahkan ke database.")

def delete_question(question):
    mycursor = mydb.cursor()
    sql = "DELETE FROM data WHERE pertanyaan = %s"
    val = (question,)
    mycursor.execute(sql, val)
    mydb.commit()
    print("Pertanyaan telah dihapus dari database.")

def lastO(pola):
    last = [-1] * 256
    for i in range(len(pola)):
        last[ord(pola[i])] = i
    return last


def searchBM(question, P):
    last = lastO(P)
    n = len(question)
    m = len(P)
    i = m - 1
    Found = False
    if i > n - 1:
        # pola > text
        hasil = -1
    else:
        j = m - 1
        Found = False
        while i < n and not Found:
            if P[j] == question[i]:
                if j == 0:
                    Found = True
                else:
                    j = j - 1
                    i = i - 1
            else:  # character jump
                lo = last[ord(question[i])]
                i = i + m - min(j, 1 + lo)
                j = m - 1

    if Found:
        hasil = i
    else:
        hasil = -1
    return hasil


def levenshtein_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

    return dp[m][n]


def main():
    while True:
        print("1. Chatbox")
        print("2. Tambahkan data Q&A")
        print("3. Hapus data Q&A")
        print("0. Berhenti")

        pilihan = input("Pilih: ")

        if pilihan == '1':
            question = input("Masukkan pertanyaan: ")

            mycursor = mydb.cursor()
            mycursor.execute("SELECT pertanyaan, jawaban FROM data")
            myresult = mycursor.fetchall()

            closest_question = ""
            closest_distance = float('inf')
            similar_questions = []

            for row in myresult:
                db_question = row[0]
                bm_result = searchBM(question, db_question)
                if bm_result != -1:
                    print("Pertanyaan ditemukan menggunakan Boyer-Moore:")
                    print("Pertanyaan:", db_question)
                    print("Jawaban:", row[1])
                    return
                else:
                    distance = levenshtein_distance(question, db_question)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_question = db_question
                        similar_questions = []  # Reset similar questions list

                    if distance == closest_distance:
                        similar_questions.append((db_question, row[1]))

            kemiripan = round(100 - closest_distance, 2)

            if (kemiripan >= 90):
                if closest_question:
                    print("Persentase kemiripan:", kemiripan, "%")
                    print("Pertanyaan terdekat:", closest_question)
                    # Mencetak data yang sesuai dengan pertanyaan terdekat
                    for row in myresult:
                        pertanyaan = row[0]
                        jawaban = row[1]
                        if pertanyaan == closest_question:
                            print("Jawaban:", jawaban)
                            print()
            else:
                similar_questions.append((db_question, row[1]))
                print("Persentase kemiripan:", kemiripan, "%")
                print("Pertanyaan tidak ada dalam database")
                print()
                print("Apakah maksud anda:")
                print()
                for i, (pertanyaan, jawaban) in enumerate(similar_questions[:3]):
                    print("- ",pertanyaan)
                    print()

        elif pilihan == '2':
            question = input("Masukkan pertanyaan: ")
            answer = input("Masukkan jawaban: ")
            add_question(question, answer)
        
        elif pilihan == '3':
            question = input("Masukkan pertanyaan yang akan dihapus: ")
            delete_question(question)

        elif pilihan == '0':
            print("Program berhenti.")
            break

        else:
            print("Pilihan tidak valid. Silakan pilih opsi yang tersedia.")

if __name__ == '__main__':
    main()
