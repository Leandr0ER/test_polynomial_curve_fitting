# Bishop 1.1: Polynomial Curve Fitting Visualization

An interactive visualization of the "Polynomial Curve Fitting" example (Chapter 1.1) from Christopher Bishop's classic book, *Pattern Recognition and Machine Learning (PRML)*.

This project demonstrates core Machine Learning concepts like **Over-fitting**, **Regularization**, and the effect of **Dataset Size** in a live, interactive environment.

## Features

- **Interactive Controls:** Adjust the number of points ($N$), polynomial degree ($M$), noise level, and regularization parameter ($\ln \lambda$) in real-time.
- **Visual Feedback:** 
  - Green Dashed Line: The true underlying function $\sin(2\pi x)$.
  - Red Solid Line: The model's current polynomial prediction.
  - Blue Circles: Data samples with Gaussian noise.
- **Model Weights:** Live display of the $w^*$ coefficients to observe weight explosion during over-fitting.
- **Tooltips:** Hover over data points to see their exact $(x, y)$ coordinates.
- **Responsive Design:** Full-screen SVG visualization that adapts to any window size.

## Tech Stack

- **Backend:** Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [NumPy](https://numpy.org/) (for Linear Algebra/Normal Equations).
- **Frontend:** [Svelte 5](https://svelte.dev/), SVG for high-performance math visualization.

## Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd test_polynomial_curve_fitting
```

### 2. Setup Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
The API will be running at `http://localhost:8000`.

### 3. Setup Frontend (Svelte)
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at the URL shown (usually `http://localhost:5173`).

## Experiments to Try

1. **Over-fitting:** Set $M=9$ and $N=10$. Notice how the red curve oscillates wildly to hit every point, losing the "true" green sine shape. Check the Sidebar to see the weights ($w^*$) growing to massive values.
2. **Regularization:** Keep $M=9, N=10$ and enable **Regularization**. Set $\ln \lambda \approx -18$. Watch the red curve smooth out and recover the sine shape.
3. **Big Data:** Disable regularization, keep $M=9$, and increase $N$ to $100$. Notice how having more data naturally prevents over-fitting even with a high-degree model.
