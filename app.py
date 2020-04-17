import psycopg2
from flask import Flask, request, redirect, render_template, url_for, flash

app = Flask(__name__)

#######################################
###       DATABASE CONNECTION       ###
#######################################

try: 
    conn = psycopg2.connect(host="pgserver.mah.se", dbname="mbdagblad", user="ah9829", password="9nir0j49")
except:
    print("Database connection failed.")

#######################################
###             HELPER              ###
#######################################

def sanitizer(text):
    """"""
    sanitized = text.replace("'", "")
    sanitized = sanitized.replace('"', '')
    sanitized = sanitized.replace ("”", "")

    return sanitized

#######################################
###             ROUTING             ###
#######################################

@app.route("/")
def index():
    """DOCSTRING"""
    articles = []

    cur = conn.cursor()
    cur.execute("SELECT id, headline, preamble, body, published FROM article ORDER BY published DESC;")
    
    columns = ["id", "headline", "preamble", "body", "published"]
    for row in cur.fetchall():
        articles.append(dict(zip(columns, row)))

    conn.commit()
    cur.close()

    return render_template("index.html", articles=articles)


# ARTICLES
@app.route("/article/new", methods=["GET", "POST"])
def new_article():
    """DOCSTRING"""
    if request.method == "POST":
        journalists = request.form.getlist("journalists")
        headline = sanitizer(request.form["headline"])
        preamble = sanitizer(request.form["preamble"])
        body = sanitizer(request.form["body"])
        image_id = request.form["image_id"]
        caption = sanitizer(request.form["caption"])

        cur = conn.cursor()

        # Article insert
        article_insert = "INSERT INTO article (headline, preamble, body) VALUES ('" + headline + "', '" + preamble + "', '" +  body + "') RETURNING id;"
        cur.execute(article_insert)
        article_id = cur.fetchone()[0]

        # Journalist inserts
        for i in journalists:
            written_by_insert = "INSERT INTO written_by (journalist_id, article_id) VALUES (" + str(i) + ", " + str(article_id) + ");"
            cur.execute(written_by_insert)

        # Article image insert
        if not image_id == "":
            image_insert = f"INSERT INTO article_image (image_id, article_id, caption) VALUES ({image_id}, {article_id}, '{caption}');"
            cur.execute(image_insert)

        conn.commit()
        cur.close()

        return redirect(url_for('index'))

    else:
        cur = conn.cursor()

        cur.execute(f"SELECT id, name FROM journalist;")
        journalists = cur.fetchall()

        cur.execute(f"SELECT id, alt_text FROM image;")
        images = cur.fetchall()

        return render_template('article-new.html', journalists=journalists, images=images)


@app.route("/article/<int:article_id>/")
def article(article_id):
    """DOCSTRING"""

    cur = conn.cursor()

    # Article
    cur.execute(f"SELECT id, headline, preamble, body, published FROM article WHERE id = {article_id};")
    #columns = ["id", "headline", "preamble", "body", "published"]
    article = cur.fetchone()
    
    # Journalists
    cur.execute(f"SELECT id, name FROM journalist JOIN written_by ON written_by.journalist_id = journalist.id WHERE written_by.article_id = {article_id}")
    #authors = ", ".join(map(lambda x: x[0], cur.fetchall()))
    authors = cur.fetchall()

    # Comments
    cur.execute(f"SELECT id, signature, published, text FROM comment WHERE article_id = {article_id};")
    comments = cur.fetchall()

    # Images
    cur.execute(f"SELECT url, alt_text, caption FROM article_image JOIN image ON image.id = article_image.image_id WHERE article_image.article_id = {article_id};")
    images = cur.fetchall()


    conn.commit()
    cur.close()
    
    return render_template("article.html", article=article, authors=authors, comments=comments, images=images)


@app.route("/article/<int:article_id>/edit", methods=["GET", "POST"])
def edit_article(article_id):
    """DOCSTRING"""
    
    if request.method == "POST":
        journalists = request.form.getlist("journalists")
        headline = sanitizer(request.form["headline"])
        preamble = sanitizer(request.form["preamble"])
        body = sanitizer(request.form["body"])
        image_id = request.form["image_id"]
        caption = sanitizer(request.form["caption"])


        cur = conn.cursor()

        # Article update
        article_update = f"UPDATE article SET headline = '{headline}', preamble = '{preamble}', body = '{body}' WHERE id = {article_id};"
        cur.execute(article_update)

        # Delete old journalists
        journalists_delete = f"DELETE FROM written_by WHERE article_id = {article_id};"
        cur.execute(journalists_delete)

        # Insert new journalists
        for i in journalists:
            written_by_insert = f"INSERT INTO written_by (journalist_id, article_id) VALUES ({str(i)}, {str(article_id)});"
            cur.execute(written_by_insert)

        # Delete old article image
        article_image_delete = f"DELETE FROM article_image WHERE article_id = {article_id};"
        cur.execute(article_image_delete)

        # Insert new article image
        if not image_id == "":
            image_insert = f"INSERT INTO article_image (image_id, article_id, caption) VALUES ({image_id}, {article_id}, '{caption}');"
            cur.execute(image_insert)

        conn.commit()
        cur.close()

        return redirect(url_for("article", article_id=article_id))

    else:
        cur = conn.cursor()

        # Get article
        cur.execute(f"SELECT id, headline, preamble, body, published FROM article WHERE id = {article_id};")
        article = cur.fetchone()

        # Get list of all journalists
        cur.execute(f"SELECT id, name FROM journalist;")
        journalists = cur.fetchall()

        # Get list of authors (ID) of this article
        cur.execute(f"SELECT journalist_id FROM written_by WHERE article_id = {article_id};")
        authors_list = cur.fetchall()

        # Flattening the list of lists to facilitate traversing in template
        authors = []
        for i in range(len(authors_list)):
            for author in range(len(authors_list[i])):
                authors.append(authors_list[i][author])

        # Get all images 
        cur.execute(f"SELECT id, alt_text FROM image;")
        images = cur.fetchall()

        # Get article image
        cur.execute(f"SELECT image_id, alt_text, caption FROM article_image JOIN image ON image.id = article_image.image_id WHERE article_image.article_id = {article_id};")        
        article_image = cur.fetchall()

        conn.commit()
        cur.close()

        return render_template("article-edit.html", article=article, journalists=journalists, authors=authors, images=images, article_image=article_image)


@app.route("/article/<int:article_id>/delete")
def delete_article(article_id):
    """DOCSTRING"""
    cur = conn.cursor()

    # Delete comments in article
    comments_delete = f"DELETE FROM comment WHERE article_id = {article_id};"
    cur.execute(comments_delete)

    # Delete entry in article_image
    article_image_delete = f"DELETE FROM article_image WHERE article_id = {article_id};"
    cur.execute(article_image_delete)

    # Delete entries in written_by table
    written_by_delete = f"DELETE FROM written_by WHERE article_id = {article_id};"
    cur.execute(written_by_delete)
    
    # Delete article
    article_delete = f"DELETE FROM article WHERE id = {article_id};"
    cur.execute(article_delete)

    conn.commit()
    cur.close()

    return redirect(url_for("index"))


# COMMENTS
@app.route("/article/<int:article_id>/comments", methods=["POST"])
def post_comment(article_id):
    """"""
    signature = sanitizer(request.form["signature"])
    text = sanitizer(request.form["text"])

    comment_insert = f"INSERT INTO comment (article_id, signature, text) VALUES ({article_id}, '{signature}', '{text}');"

    cur = conn.cursor()
    cur.execute(comment_insert)
    conn.commit()
    cur.close()

    return redirect(url_for("article", article_id=article_id))


@app.route("/article/<int:article_id>/comment/<int:comment_id>/delete")
def delete_comment(article_id, comment_id):
    """"""
    sql_query = f"DELETE FROM comment WHERE article_id = {article_id} AND id = {comment_id};"

    cur = conn.cursor()
    cur.execute(sql_query)
    conn.commit()
    cur.close()

    return redirect(url_for("article", article_id=article_id))


# IMAGES
@app.route("/images")
def images():
    """"""
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM image ORDER BY published DESC;")
    images = cur.fetchall()

    conn.commit()
    cur.close()

    return render_template("images.html", images=images)


@app.route("/image/new", methods=["GET", "POST"])
def new_image():
    """"""
    if request.method == "POST":
        url = sanitizer(request.form["url"])
        alt = sanitizer(request.form["alt"])

        image_insert = "INSERT INTO image (url, alt_text) VALUES ('" + url + "', '" + alt + "');"

        cur = conn.cursor()
        cur.execute(image_insert)
        conn.commit()
        cur.close()

        return redirect(url_for("images"))

    else:
        return render_template("image-new.html")

@app.route("/image/<int:image_id>/delete")
def delete_image(image_id):
    """"""
    cur = conn.cursor()

    # Delete article_image entries
    article_image_delete = f"DELETE FROM article_image WHERE image_id = {image_id};"
    cur.execute(article_image_delete)

    # Delete image
    image_delete = f"DELETE FROM image WHERE id = {image_id};"
    cur.execute(image_delete)

    conn.commit()
    cur.close()

    return redirect(url_for('images'))


# JOURNALISTS
@app.route("/journalists")
def journalists():
    """"""
    cur = conn.cursor()

    cur.execute("SELECT id, name, note FROM journalist;")
    journalists = cur.fetchall()

    conn.commit()
    cur.close()

    return render_template("journalists.html", journalists=journalists)


@app.route("/journalist/<int:journalist_id>/")
def journalist(journalist_id):
    """"""
    cur = conn.cursor()

    cur.execute(f"SELECT id, name, note FROM journalist WHERE id = {journalist_id};")
    journalist = cur.fetchone()

    cur.execute(f"SELECT id, headline, preamble, published FROM article JOIN written_by ON written_by.article_id = article.id WHERE written_by.journalist_id = {journalist_id};")
    articles = cur.fetchall()

    conn.commit()
    cur.close()
    
    return render_template("journalist.html", journalist=journalist, articles=articles)


@app.route("/journalist/new", methods=["POST", "GET"])
def new_journalist():
    """"""
    if request.method == "POST":
        name = sanitizer(request.form["name"])
        pnr = sanitizer(request.form["pnr"])
        note = sanitizer(request.form["note"])

        journalist_insert = f"INSERT INTO journalist (pnr, name, note) VALUES ('{pnr}', '{name}', '{note}');"

        cur = conn.cursor()
        cur.execute(journalist_insert)
        conn.commit()
        cur.close()

        return redirect(url_for("journalists"))

    else:
        return render_template("journalist-new.html")


@app.route("/journalist/<int:journalist_id>/edit", methods=["POST", "GET"])
def edit_journalist(journalist_id):
    """"""
    if request.method == "POST":
        cur = conn.cursor()

        name = request.form["name"]
        pnr = request.form["pnr"]
        note = request.form["note"]

        journalist_edit = f"UPDATE journalist SET name = '{name}', pnr = '{pnr}', note = '{note}' WHERE id = {journalist_id};"
        cur.execute(journalist_edit)
        conn.commit()
        cur.close()

        return redirect(url_for("journalist", journalist_id=journalist_id))
    else:
        cur = conn.cursor()

        journalist_select = f"SELECT * FROM journalist WHERE id = {journalist_id};"
        cur.execute(journalist_select)
        journalist = cur.fetchone()

        return render_template("journalist-edit.html", journalist=journalist)




@app.route("/journalist/<int:journalist_id>/delete")
def delete_journalist(journalist_id):
    """"""
    cur = conn.cursor()

    # Delete entries in written_by table
    written_by_delete = f"DELETE FROM written_by WHERE journalist_id = {journalist_id};"
    cur.execute(written_by_delete)

    # Delete journalist
    journalist_delete = f"DELETE FROM journalist WHERE id = {journalist_id};"
    cur.execute(journalist_delete)

    conn.commit()
    cur.close()

    return redirect(url_for("journalists"))


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)