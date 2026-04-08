from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Optional

app = FastAPI()

# CORS configuration to allow requests from Svelte (usually port 5173 or 4173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FittingParams(BaseModel):
    N: int = 10         # Number of data points
    M: int = 9          # Polynomial degree
    ln_lambda: Optional[float] = None  # Regularization parameter (ln lambda)
    noise_level: float = 0.2

def get_phi(x: np.ndarray, M: int) -> np.ndarray:
    """Calculates the design matrix Phi of size (N, M+1)"""
    phi = np.zeros((len(x), M + 1))
    for i in range(M + 1):
        phi[:, i] = x**i
    return phi

@app.post("/fit")
async def fit_polynomial(params: FittingParams):
    # 1. Generate N equidistant points in [0, 1] as in the book (Fig 1.2)
    x = np.linspace(0, 1, params.N)
    
    # 2. t = sin(2*pi*x) + Gaussian noise
    np.random.seed(42) # Fixed seed for visual consistency when moving sliders
    noise = np.random.normal(0, params.noise_level, params.N)
    t = np.sin(2 * np.pi * x) + noise
    
    # 3. Calculate weights w* (Bishop's Equation 1.4 + 1.12)
    phi = get_phi(x, params.M)
    
    # Using np.linalg.solve instead of inv() for numerical stability
    A = phi.T @ phi
    b = phi.T @ t
    
    if params.ln_lambda is not None:
        # Regularization: (Phi^T Phi + lambda * I) w = Phi^T t
        lam = np.exp(params.ln_lambda)
        A += lam * np.identity(params.M + 1)
    
    # Solve the linear system
    try:
        w = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        # Fallback to pseudo-inverse if matrix is singular
        w = np.linalg.pinv(phi) @ t
        
    # 4. Generate smooth curve for visualization (100 points)
    x_plot = np.linspace(0, 1, 100)
    phi_plot = get_phi(x_plot, params.M)
    y_plot = phi_plot @ w
    
    # Target function sin(2*pi*x)
    y_real = np.sin(2 * np.pi * x_plot)
    
    return {
        "points": [{"x": xi, "t": ti} for xi, ti in zip(x, t)],
        "fitted_curve": [{"x": xi, "y": yi} for xi, yi in zip(x_plot, y_plot)],
        "real_curve": [{"x": xi, "y": yi} for xi, yi in zip(x_plot, y_real)],
        "weights": w.tolist()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
