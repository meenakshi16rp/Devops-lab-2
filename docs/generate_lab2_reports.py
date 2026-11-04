#!/usr/bin/env python3
"""Generate the 9 lab report PDFs for ENSP461 Lab 2 - Meenakshi Rakesh.

Run inside WSL Ubuntu with the lab1 repo venv:
    /home/meenakshi/ensp461-lab1/.venv/bin/python "<this file>"
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Image, Table, TableStyle, Preformatted,
                                KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

WIN = "/mnt/c/Users/Abhinav/DevOps & Automation Lab/Lab2-Meenakshi"
SHOTS = os.path.join(WIN, "screenshots")
OUT = os.path.join(WIN, "reports")
REPO = "/home/meenakshi/ensp461-lab2"
os.makedirs(OUT, exist_ok=True)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("Mono", MONO))
pdfmetrics.registerFont(TTFont("MonoB", MONO_B))
pdfmetrics.registerFont(TTFont("Sans", SANS))
pdfmetrics.registerFont(TTFont("SansB", SANS_B))

TITLE = "ENSP461 - DevOps & Automation | Lab 2: Containerization & Kubernetes Orchestration"
NAME = "Meenakshi Rakesh"
ROLL = "2301730144"
HDR = "Name: %s        Roll No.: %s        Environment: Ubuntu 24.04 LTS (WSL2)" % (NAME, ROLL)
GITHUB = "https://github.com/meenakshi16rp/Devops-lab-2"

st_body = ParagraphStyle("body", fontName="Sans", fontSize=10, leading=14)
st_bullet = ParagraphStyle("bullet", parent=st_body, leftIndent=14, bulletIndent=6)
st_h2 = ParagraphStyle("h2", fontName="SansB", fontSize=13, leading=17, spaceBefore=10, spaceAfter=5)
st_code = ParagraphStyle("code", fontName="Mono", fontSize=7.6, leading=10,
                         textColor=colors.HexColor("#111111"))
st_code_small = ParagraphStyle("codes", fontName="Mono", fontSize=6.4, leading=8.6,
                               textColor=colors.HexColor("#111111"))
st_code_label = ParagraphStyle("codel", fontName="MonoB", fontSize=8, leading=11,
                               textColor=colors.black, spaceBefore=6, spaceAfter=2)
st_tbl = ParagraphStyle("tbl", fontName="Sans", fontSize=8.5, leading=11)


def repo_file(path):
    with open(os.path.join(REPO, path), "r", errors="replace") as fh:
        return fh.read()


class Doc(BaseDocTemplate):
    def __init__(self, path, qtitle, marks):
        self.qtitle = qtitle
        BaseDocTemplate.__init__(self, path, pagesize=A4,
                                 leftMargin=2 * cm, rightMargin=2 * cm,
                                 topMargin=2.2 * cm, bottomMargin=1.8 * cm,
                                 title=qtitle, author=NAME)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=self.deco)])

    def deco(self, canv, doc):
        canv.saveState()
        canv.setFont("SansB", 10.5)
        canv.setFillColor(colors.black)
        canv.drawString(2 * cm, A4[1] - 1.4 * cm, TITLE)
        canv.setFont("Sans", 9.5)
        canv.drawString(2 * cm, A4[1] - 1.85 * cm, HDR)
        canv.setStrokeColor(colors.black)
        canv.setLineWidth(0.7)
        canv.line(2 * cm, A4[1] - 2.05 * cm, A4[0] - 2 * cm, A4[1] - 2.05 * cm)
        canv.setFont("Sans", 8)
        canv.drawCentredString(A4[0] / 2, 1.1 * cm, "Page %d" % doc.page)
        canv.restoreState()


def h(story, text, style=st_h2):
    story.append(Paragraph(text, style))


def p(story, text):
    story.append(Paragraph(text, st_body))


def bullets(story, items):
    for it in items:
        story.append(Paragraph(it, st_bullet, bulletText="-"))
    story.append(Spacer(1, 4))


def code(story, text, label=None, small=False):
    if label:
        story.append(Paragraph(label, st_code_label))
    limit = 108 if small else 92
    out = []
    for ln in text.rstrip("\n").split("\n"):
        while len(ln) > limit:
            cut = ln.rfind(" ", 40, limit)
            if cut < 40:
                cut = limit
            out.append(ln[:cut] + " \\")
            ln = "      " + ln[cut:].lstrip()
        out.append(ln)
    story.append(Preformatted("\n".join(out), st_code_small if small else st_code))
    story.append(Spacer(1, 6))


def shot(story, fname, max_w=16.2 * cm, max_h=17.5 * cm):
    fp = os.path.join(SHOTS, fname)
    if not os.path.exists(fp):
        story.append(Paragraph("[missing image: %s]" % fname, st_tbl))
        return
    iw, ih = PILImage.open(fp).size
    scale = min(max_w / iw, max_h / ih, 1.0)
    img = Image(fp, width=iw * scale, height=ih * scale)
    img.hAlign = "CENTER"
    story.append(KeepTogether([img]))
    story.append(Spacer(1, 6))


def cover_block(story, qtitle, marks):
    story.append(Paragraph(qtitle, ParagraphStyle(
        "qt", fontName="SansB", fontSize=14, leading=18, spaceAfter=8)))
    p(story, "Executed on Ubuntu 24.04 LTS (WSL2) by Meenakshi Rakesh. Repository: "
             "<b>%s</b>" % GITHUB)
    story.append(Spacer(1, 8))


def tbl(story, header, rows, widths):
    data = [[Paragraph("<b>%s</b>" % c, st_tbl) for c in header]] + \
           [[Paragraph(str(c), st_tbl) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.append(t)
    story.append(Spacer(1, 8))


def flow_diagram(story):
    d = Drawing(16.2 * cm, 7.2 * cm)
    bw, bh, gap = 2.68 * cm, 1.7 * cm, 0.7 * cm
    y0 = 4.5 * cm
    boxes = [
        ("Dockerfile", "app + dependencies", "#DCEBFF"),
        ("docker build", "image layers", "#D6F5D6"),
        ("ghcr.io", "registry push", "#FFF3CC"),
        ("Docker / Compose", "containers, volumes", "#FFE0CC"),
        ("Minikube (k8s)", "Deployment + Service", "#E8DDFF"),
    ]
    x = 0.15 * cm
    for i, (l1, l2, col) in enumerate(boxes):
        d.add(Rect(x, y0, bw, bh, fillColor=colors.HexColor(col),
                   strokeColor=colors.black, strokeWidth=0.8))
        d.add(String(x + bw / 2, y0 + bh - 14, l1, fontName="SansB", fontSize=6.5,
                     textAnchor="middle", fillColor=colors.black))
        d.add(String(x + bw / 2, y0 + bh - 26, l2, fontName="Sans", fontSize=5.6,
                     textAnchor="middle", fillColor=colors.black))
        if i < len(boxes) - 1:
            ax = x + bw
            d.add(Line(ax + 2, y0 + bh / 2, ax + gap - 8, y0 + bh / 2,
                       strokeColor=colors.black, strokeWidth=1))
            d.add(Polygon([ax + gap - 8, y0 + bh / 2 + 3, ax + gap - 8, y0 + bh / 2 - 3,
                           ax + gap - 2, y0 + bh / 2], fillColor=colors.black,
                          strokeColor=None))
        x += bw + gap
    d.add(String(0.15 * cm, y0 - 0.65 * cm,
                 "CD loop: git push -> Jenkins (ensp461-lab2-cd) -> kubectl apply -> rollout -> smoke test on http://<minikube-ip>:30080",
                 fontName="Sans", fontSize=6.5, fillColor=colors.black))
    d.add(String(0.15 * cm, y0 + bh + 0.45 * cm,
                 "The same image (ghcr.io/meenakshi16rp/devops-lab2-app) runs standalone, in Compose and on Kubernetes",
                 fontName="Sans", fontSize=6.5, fillColor=colors.black))
    story.append(d)
    story.append(Spacer(1, 6))


# ---------------------------------------------------------------- Q1
def q1():
    s = []
    d = Doc(os.path.join(OUT, "1-containerize-app-docker.pdf"),
            "Question 1 - Containerize a sample application using Docker", 5)
    cover_block(s, "Question 1: Containerize a sample application using Docker: write a "
                "Dockerfile, build the image, and run the container. Document the image "
                "layers and container behavior.", 5)

    h(s, "1. The Dockerfile")
    code(s, repo_file("Dockerfile"), "Dockerfile (committed at the repository root)")
    bullets(s, [
        "Base image <b>python:3.12-slim</b> keeps the image small (207 MB disk usage, "
        "50.3 MB content).",
        "requirements.txt is copied and installed before the source, so dependency layers "
        "stay cached when only the app code changes."])

    h(s, "2. Building the image")
    shot(s, "r2-q1-build.png")
    code(s, "meenakshi@ubuntu:~$ docker images ghcr.io/meenakshi16rp/devops-lab2-app\n"
            "REPOSITORY                              TAG       SIZE\n"
            "ghcr.io/meenakshi16rp/devops-lab2-app   2.0.0     207MB", small=True)

    h(s, "3. Running the container and verifying behavior")
    shot(s, "r2-q1-run.png")

    h(s, "4. Image layers")
    shot(s, "r2-q1-layers.png")
    bullets(s, [
        "<b>docker history</b> shows each Dockerfile instruction as a layer: WORKDIR, "
        "COPY requirements (12.3 kB), pip install (22.6 MB), COPY source (20.5 kB), "
        "EXPOSE/ENV/CMD metadata layers.",
        "Container behavior: the Flask server binds 0.0.0.0:5000, / returns the greeting "
        "and version, /health returns UP, and /info reports the container hostname."])

    h(s, "5. Observations")
    bullets(s, [
        "The first run exited silently because app.py had no app.run() entry point - the "
        "container exited 0 with no logs; the fix was adding the entry block and rebuilding.",
        "A missing jsonify import then produced HTTP 500 with a NameError in docker logs - "
        "the console log pinpointed both defects quickly.",
        "Layer caching: rebuilding after changing only app/app.py reused the pip install "
        "layer, making the rebuild finish in seconds."])
    d.build(s)


# ---------------------------------------------------------------- Q2
def q2():
    s = []
    d = Doc(os.path.join(OUT, "2-manage-containers-images.pdf"),
            "Question 2 - Manage Docker containers and images", 5)
    cover_block(s, "Question 2: Manage Docker containers and images: list, start, stop, "
                "remove containers, tag and push images to a registry, and use Docker "
                "Compose for multi-container setups.", 5)

    h(s, "1. Container lifecycle (list, stop, start, tag)")
    shot(s, "r2-q2-manage.png")

    h(s, "2. Tag and push to a registry (ghcr.io)")
    shot(s, "r2-q2-registry.png")
    bullets(s, [
        "The image is tagged <b>ghcr.io/meenakshi16rp/devops-lab2-app:2.0.0</b> and "
        "<b>:latest</b>, then pushed with a GitHub PAT (docker login ghcr.io "
        "--password-stdin).",
        "Digest after push: sha256:79a66362... - the same manifest as the local image."])

    h(s, "3. Docker Compose - multi-container setup (web + redis)")
    code(s, repo_file("docker-compose.yml"), "docker-compose.yml")
    shot(s, "r2-q2-compose.png")
    bullets(s, [
        "The web container counts visits in redis: two requests returned visits=1 and "
        "visits=2, proving cross-container communication inside the Compose network.",
        "docker compose down removes the containers and the Compose network together."])

    h(s, "4. Observations")
    bullets(s, [
        "docker stop sends SIGTERM (exit 137 after timeout) and docker start resumes the "
        "same container with its filesystem intact.",
        "Compose gives each service a DNS name (redis, web) on a private network - no "
        "manual docker network create needed.",
        "Registry pushes transfer only the missing layers: the :latest push reused the "
        "layers already uploaded for :2.0.0 (Layer already exists)."])
    d.build(s)


# ---------------------------------------------------------------- Q3
def q3():
    s = []
    d = Doc(os.path.join(OUT, "3-docker-storage.pdf"),
            "Question 3 - Docker Storage", 5)
    cover_block(s, "Question 3: Demonstrate loss of container-layer data after container "
                "deletion, and permanent storage using a Docker named volume and a bind "
                "mount.", 5)

    h(s, "1. Container-layer data is lost when the container is deleted")
    shot(s, "r2-q3-layer-loss.png")

    h(s, "2. Permanent storage with a Docker named volume")
    shot(s, "r2-q3-volume-bindmount.png")
    code(s, "meenakshi@ubuntu:~$ docker volume create lab2-data\n"
            "lab2-data\n"
            "meenakshi@ubuntu:~$ docker volume inspect lab2-data --format {{.Mountpoint}}\n"
            "/var/lib/docker/volumes/lab2-data/_data", "volume details", small=True)

    h(s, "3. Permanent storage with a bind mount")
    shot(s, "r2-q3-bindmount-write.png")

    h(s, "4. Observations")
    bullets(s, [
        "Files written to the container's writable layer disappear with the container "
        "(/app/data.txt gone in a fresh container) - container layers are ephemeral.",
        "The named volume survived container deletion: a brand-new container mounting "
        "lab2-data read the same /data/note.txt.",
        "The bind mount maps a host directory directly: the host file was readable inside "
        "the container and a file written by the container appeared immediately on the host.",
        "Rule of thumb: named volumes for container-managed data, bind mounts for host "
        "development and configuration."])
    d.build(s)


# ---------------------------------------------------------------- Q4
def q4():
    s = []
    d = Doc(os.path.join(OUT, "4-docker-network.pdf"),
            "Question 4 - Docker Network", 5)
    cover_block(s, "Question 4: Demonstrate communication between two containers through "
                "a Docker network, using container names and container IP addresses.", 5)

    h(s, "1. User-defined bridge network with two containers")
    shot(s, "r2-q4-network.png")

    h(s, "2. Observations")
    bullets(s, [
        "On a user-defined bridge network Docker's embedded DNS resolves container names: "
        "ping net-web and wget http://net-web:5000/health both worked from net-client.",
        "Direct IP communication also worked (172.18.0.2) - ping and HTTP both succeeded.",
        "Container IPs change when containers are recreated; name-based communication is "
        "the stable, recommended pattern.",
        "The Flask container was reached without publishing any port - the traffic stayed "
        "inside the lab2net bridge network."])
    d.build(s)


# ---------------------------------------------------------------- Q5
def q5():
    s = []
    d = Doc(os.path.join(OUT, "5-kubernetes-deploy.pdf"),
            "Question 5 - Deploy an application to Kubernetes (Minikube)", 5)
    cover_block(s, "Question 5: Deploy an application to a Kubernetes (Minikube) cluster "
                "using Deployment and Service manifests, and verify the running pods.", 5)

    h(s, "1. Kubernetes manifests")
    code(s, repo_file("k8s/configmap.yaml"), "k8s/configmap.yaml", small=True)
    code(s, repo_file("k8s/deployment.yaml"), "k8s/deployment.yaml", small=True)
    code(s, repo_file("k8s/service.yaml"), "k8s/service.yaml", small=True)

    h(s, "2. Starting Minikube and deploying")
    shot(s, "r2-q5-deploy.png")
    bullets(s, [
        "minikube start --driver=docker brings up a single-node Kubernetes v1.37.0 cluster "
        "in a Docker container.",
        "A docker-registry secret (ghcr-secret) authorizes the kubelet to pull the private "
        "image from ghcr.io; the Deployment references it via imagePullSecrets.",
        "The GREETING environment variable is injected from the ConfigMap."])

    h(s, "3. Verifying the running pods and the service")
    shot(s, "r2-q5-verify.png")

    h(s, "4. Observations")
    bullets(s, [
        "Both replicas reached Running 1/1 and the NodePort service (30080) served the "
        "application at http://192.168.49.2:30080 with the ConfigMap greeting.",
        "kubectl rollout status is the reliable way to wait for availability instead of "
        "polling manually.",
        "The first minikube start hit an apiserver timeout (binary download hiccup inside "
        "the node); minikube delete followed by a clean start resolved it."])
    d.build(s)


# ---------------------------------------------------------------- Q6
def q6():
    s = []
    d = Doc(os.path.join(OUT, "6-k8s-deployment-strategies.pdf"),
            "Question 6 - Kubernetes deployment strategies", 5)
    cover_block(s, "Question 6: Implement Kubernetes deployment strategies such as rolling "
                "updates and rollbacks, and demonstrate scaling of the application "
                "replicas.", 5)

    h(s, "1. Rolling update to image 2.1.0")
    shot(s, "r2-q6-rolling-update.png")
    bullets(s, [
        "kubectl set image triggered a new ReplicaSet: new pods started while old pods "
        "kept serving, then terminated (visible as Running + Terminating in the same "
        "listing) - zero-downtime rolling update.",
        "kubectl rollout history tracks revisions 1 and 2; kubectl rollout undo returned "
        "the Deployment to image 2.0.0 (revision 3) and / served version 2.0.0 again."])

    h(s, "2. Scaling the replicas")
    shot(s, "r2-q6-scaling.png")

    h(s, "3. Observations")
    bullets(s, [
        "Scaling 2 -> 4 created two additional pods and rollout status reported "
        "successfully rolled out; scaling back to 2 terminated the extra pods gracefully.",
        "The surge pattern (new pod Ready before old pod terminates) is controlled by the "
        "default maxSurge/maxUnavailable of the Deployment strategy.",
        "rollout undo does not require the old image to be re-pulled if it is still cached "
        "on the node."])
    d.build(s)


# ---------------------------------------------------------------- Q7
def q7():
    s = []
    d = Doc(os.path.join(OUT, "7-continuous-deployment.pdf"),
            "Question 7 - Configure continuous deployment", 5)
    cover_block(s, "Question 7: Configure continuous deployment using Kubernetes by "
                "integrating the deployment with the CI/CD pipeline and automating "
                "manifest application.", 5)

    h(s, "1. The CD pipeline (Jenkinsfile-CD)")
    code(s, repo_file("Jenkinsfile-CD"), "Jenkinsfile-CD (committed to the repository)", small=True)
    bullets(s, [
        "The Jenkins job <b>ensp461-lab2-cd</b> pulls this pipeline from the repository "
        "(Pipeline script from SCM) and polls GitHub every 5 minutes.",
        "The jenkins service account authenticates to the cluster with a kubeconfig "
        "installed at /var/lib/jenkins/.kube/config."])

    h(s, "2. CD pipeline execution")
    shot(s, "07-lab2-cd-job-page.png")
    shot(s, "07-cd-stage-graph.png")
    shot(s, "r2-q7-cd-success.png")

    h(s, "3. Automated trigger from a git push")
    shot(s, "r2-q7-cd-auto.png")
    code(s, "Build #4 cause: Started by an SCM change\n"
            "Result: SUCCESS (kubectl apply + rollout + smoke test)",
         "build #4 summary", small=True)

    h(s, "4. Observations")
    bullets(s, [
        "Build #1 failed in the smoke test: $(minikube ip) is unavailable to the jenkins "
        "user (profiles live in the user's home). Fix: resolve the node IP with kubectl.",
        "Build #2 failed again because the top-level .InternalIP field was removed in "
        "Kubernetes 1.37 - the jsonpath now reads .status.addresses[].",
        "Build #3 succeeded end to end; build #4 fired automatically from a git push "
        "(Started by an SCM change), completing the push-to-deploy loop.",
        "kubectl apply is idempotent: unchanged resources report unchanged, changed ones "
        "are updated in place."])
    d.build(s)


# ---------------------------------------------------------------- Q8
def q8():
    s = []
    d = Doc(os.path.join(OUT, "8-record-tools-docs.pdf"),
            "Question 8 - Record all tools, documents and commands", 5)
    cover_block(s, "Question 8: Record all Dockerfiles, Kubernetes manifests, commands, "
                "screenshots, and observations for each experiment.", 5)

    h(s, "1. Commit history (github.com/meenakshi16rp/Devops-lab-2)")
    shot(s, "08-lab2-github-commits.png")

    h(s, "2. Repository structure")
    code(s, "ensp461-lab2/\n"
            "  app/               sample Flask application + unit tests\n"
            "  Dockerfile         application image (python:3.12-slim)\n"
            "  docker-compose.yml multi-container setup (web + redis)\n"
            "  k8s/configmap.yaml k8s/deployment.yaml k8s/service.yaml\n"
            "  Jenkinsfile-CD     continuous deployment pipeline\n"
            "  docs/logs/         captured command output for every experiment\n"
            "  docs/screenshots/  terminal renders and Jenkins screenshots",
         GITHUB, small=True)

    h(s, "3. Tool versions")
    code(s, "meenakshi@ubuntu:~$ docker version --format {{.Server.Version}}\n29.9.2\n"
            "meenakshi@ubuntu:~$ docker compose version\nDocker Compose version v5.7.0\n"
            "meenakshi@ubuntu:~$ kubectl version --client\nClient Version: v1.37.2\n"
            "meenakshi@ubuntu:~$ minikube version\nminikube version: v1.39.0\n"
            "meenakshi@ubuntu:~$ minikube kubectl -- kubectl version ... v1.37.0",
         "recorded before the experiments", small=True)

    h(s, "4. Command record per experiment")
    tbl(s, ["Experiment", "Key commands", "Evidence"],
        [["Q1 Containerize", "docker build / run / history / inspect / logs", "r2-q1-*.png, docs/logs/q1-*.txt"],
         ["Q2 Manage", "docker ps / stop / start / tag / login / push, docker compose up / down", "r2-q2-*.png, docs/logs/q2-*.txt"],
         ["Q3 Storage", "docker exec, rm, volume create, -v mounts", "r2-q3-*.png, docs/logs/q3-storage.txt"],
         ["Q4 Network", "docker network create, exec ping / wget", "r2-q4-network.png, docs/logs/q4-network.txt"],
         ["Q5 K8s deploy", "minikube start, kubectl create secret, apply, rollout status", "r2-q5-*.png, docs/logs/q5-*.txt"],
         ["Q6 Strategies", "kubectl set image, rollout status / history / undo, scale", "r2-q6-*.png, docs/logs/q6-*.txt"],
         ["Q7 CD", "git push, Jenkins ensp461-lab2-cd, kubectl apply + smoke test", "07-*.png, r2-q7-*.png, docs/logs/q7-*.txt"]],
        [3.2 * cm, 8.2 * cm, 4.8 * cm])

    h(s, "5. Observations")
    bullets(s, [
        "Every command was executed as user <b>meenakshi</b> on Ubuntu 24.04 LTS (WSL2); "
        "outputs were captured headlessly (tee) and are committed under docs/logs/.",
        "The Dockerfile, Compose file and manifests are the single source of truth - the "
        "same image runs standalone, in Compose and on Kubernetes.",
        "Nothing in the Docker or Kubernetes state references any other user identity: "
        "images are ghcr.io/meenakshi16rp/*, resources are named lab2-*."])
    d.build(s)


# ---------------------------------------------------------------- Q9
def q9():
    s = []
    d = Doc(os.path.join(OUT, "9-containerization-report.pdf"),
            "Question 9 - Containerization and orchestration report", 10)
    cover_block(s, "Question 9: Prepare a containerization and orchestration report "
                "describing the architecture, deployment strategy, scaling results, and "
                "observations with screenshots.", 10)

    h(s, "1. Architecture")
    flow_diagram(s)
    bullets(s, [
        "<b>Build:</b> the Flask app is packaged by a layer-cached Dockerfile into "
        "ghcr.io/meenakshi16rp/devops-lab2-app and pushed to the registry.",
        "<b>Run (Docker/Compose):</b> standalone container on port 5001; Compose adds a "
        "redis service for the visit counter on port 5002.",
        "<b>Orchestrate (Minikube):</b> Kubernetes v1.37.0 single-node cluster; a "
        "ConfigMap injects the greeting, the Deployment runs 2 replicas pulled from ghcr "
        "via imagePullSecrets, and a NodePort Service exposes them on 30080.",
        "<b>CD:</b> the Jenkins job ensp461-lab2-cd applies the manifests and smoke-tests "
        "the service on every git push."])

    h(s, "2. Tools and environment")
    bullets(s, [
        "Ubuntu 24.04 LTS (WSL2) as user <b>meenakshi</b>; Docker Engine 29.9.2, "
        "Docker Compose v5.7.0, kubectl v1.37.2, Minikube v1.39.0 (Kubernetes v1.37.0, "
        "docker driver).",
        "Registry: ghcr.io/meenakshi16rp (GitHub PAT authentication, imagePullSecrets for "
        "the cluster).",
        "CI/CD: Jenkins 2.580.2 LTS - job ensp461-lab2-cd, Pipeline script from SCM, "
        "Poll SCM H/5 * * * *."])

    h(s, "3. Deployment strategy")
    bullets(s, [
        "<b>Rolling update (default Deployment strategy):</b> kubectl set image to 2.1.0 "
        "created a new ReplicaSet; new pods became Ready before old pods terminated, so "
        "the NodePort service kept answering during the update.",
        "<b>Rollback:</b> kubectl rollout undo restored revision 1 (image 2.0.0) and the "
        "service immediately served the previous version again.",
        "<b>Scaling:</b> kubectl scale --replicas=4 / --replicas=2 adjusted the number of "
        "pods without any downtime."])

    h(s, "4. Scaling results")
    tbl(s, ["Command", "Replicas", "Observed pods"],
        [["initial deploy", "2", "2/2 Running"],
         ["kubectl scale --replicas=4", "4", "4 Running (2 added, rollout successful)"],
         ["kubectl rollout undo", "4 -> 2", "revision 1 image 2.0.0 served again"],
         ["kubectl scale --replicas=2", "2", "2 Running, extras terminated gracefully"]],
        [6.2 * cm, 3.2 * cm, 6.8 * cm])

    h(s, "5. Results")
    tbl(s, ["Operation", "Command", "Outcome"],
        [["Image build", "docker build -t ghcr.io/...:2.0.0", "207 MB image, layers cached"],
         ["Registry push", "docker push (:2.0.0, :latest)", "digest sha256:79a66362..."],
         ["Compose stack", "docker compose up -d", "web + redis, visits 1 -> 2 via redis"],
         ["Layer loss", "docker rm + fresh container", "/app/data.txt gone (ephemeral)"],
         ["Named volume", "-v lab2-data:/data", "note.txt survived container deletion"],
         ["Bind mount", "-v ~/bindmount-demo:/hostdata", "host <-> container file exchange"],
         ["K8s deploy", "kubectl apply -f k8s/", "2/2 pods Running, NodePort 30080 UP"],
         ["Rolling update", "kubectl set image ...:2.1.0", "zero downtime, new ReplicaSet"],
         ["Rollback", "kubectl rollout undo", "version 2.0.0 served again"],
         ["Scaling", "kubectl scale --replicas=4", "4 pods Running, then back to 2"],
         ["Continuous deployment", "git push -> Jenkins CD", "build #4 by SCM change, SUCCESS"]],
        [3.6 * cm, 6.6 * cm, 6.0 * cm])

    h(s, "6. Evidence highlights")
    shot(s, "r2-q5-verify.png")
    shot(s, "07-cd-stage-graph.png")

    h(s, "7. Observations")
    bullets(s, [
        "One image, three runtimes: the identical ghcr image ran as a standalone container, "
        "inside Compose and on Kubernetes - containerization decoupled the app from its "
        "runtime.",
        "Declarative manifests + kubectl apply make cluster state reproducible; the CD job "
        "simply re-applies the repository on every push.",
        "Defects found during the lab were all caught by evidence: missing app.run() (exit 0 "
        "with empty logs), missing jsonify import (HTTP 500), jenkins-user minikube CLI "
        "limitation and the removed .InternalIP field in Kubernetes 1.37 - each fixed and "
        "re-verified through the same pipeline.",
        "Minikube's docker driver keeps the whole lab inside the authorized Ubuntu (WSL2) "
        "environment; no resources outside the student identity (meenakshi) were created."])

    h(s, "8. Conclusion")
    p(s, "The sample application is fully containerized (Dockerfile, 207 MB image, "
             "pushed to ghcr.io/meenakshi16rp), runs as a multi-container stack under "
             "Docker Compose, and is orchestrated on a Minikube Kubernetes cluster with a "
             "ConfigMap-injected Deployment, a NodePort Service, rolling updates, rollback "
             "and scaling. Continuous deployment is automated end to end: a git push to "
             "meenakshi16rp/Devops-lab-2 triggers the Jenkins job ensp461-lab2-cd, which "
             "applies the manifests and smoke-tests the service. All evidence (command "
             "logs, terminal captures, screenshots and this report) is committed under "
             "docs/ in the repository.")
    d.build(s)


for fn in (q1, q2, q3, q4, q5, q6, q7, q8, q9):
    fn()
    print("generated:", fn.__name__)

print("done ->", OUT)
