#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Thư viện sinh hình vẽ toán học trực quan độ nét cao (300 DPI)
phục vụ biên soạn bài giảng và cẩm nang lý thuyết MathPlus Academy.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Polygon, Rectangle

plt.rcParams['font.sans-serif'] = ['Arial', 'Segoe UI', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def plot_unit_circle_related_angles(alpha_deg=35, mode="pi_plus_alpha", save_path="unit_circle.png"):
    """Vẽ đường tròn lượng giác giải thích cung liên kết (Hơn kém pi, bù nhau, đối nhau)."""
    fig, ax = plt.subplots(figsize=(9, 9), dpi=300)
    theta = np.linspace(0, 2 * np.pi, 500)
    ax.plot(np.cos(theta), np.sin(theta), color='#0F172A', linewidth=2.2)

    ax.axhline(0, color='#334155', linewidth=1.5)
    ax.axvline(0, color='#334155', linewidth=1.5)
    ax.annotate('', xy=(1.35, 0), xytext=(-1.35, 0), arrowprops=dict(arrowstyle="-|>", color='#334155', lw=1.8))
    ax.annotate('', xy=(0, 1.35), xytext=(0, -1.35), arrowprops=dict(arrowstyle="-|>", color='#334155', lw=1.8))

    ax.text(1.38, 0.04, 'Trục cos (Ox)', fontsize=11, fontweight='bold', color='#0F172A', va='bottom')
    ax.text(0.04, 1.38, 'Trục sin (Oy)', fontsize=11, fontweight='bold', color='#0F172A', ha='left')
    ax.text(-0.06, -0.06, 'O', fontsize=12, fontweight='bold', color='#334155', ha='right', va='top')

    alpha = np.radians(alpha_deg)
    x1, y1 = np.cos(alpha), np.sin(alpha)
    ax.plot([0, x1], [0, y1], color='#0284C7', lw=2)
    ax.scatter([x1], [y1], color='#0284C7', s=70, zorder=5)
    ax.text(x1 + 0.04, y1 + 0.04, r'$M(\cos\alpha, \sin\alpha)$', fontsize=11, fontweight='bold', color='#0284C7')

    if mode == "pi_plus_alpha":
        alpha_p = np.pi + alpha
        x2, y2 = np.cos(alpha_p), np.sin(alpha_p)
        ax.plot([0, x2], [0, y2], color='#DC2626', lw=2)
        ax.scatter([x2], [y2], color='#DC2626', s=70, zorder=5)
        ax.text(x2 - 0.05, y2 - 0.05, r"$M'(-\cos\alpha, -\sin\alpha)$", fontsize=11, fontweight='bold', color='#DC2626', ha='right', va='top')
        ax.plot([x2, x1], [y2, y1], color='#1E293B', lw=1.5, ls='--')
        plt.title(r"ĐƯỜNG TRÒN LƯỢNG GIÁC: $\sin(\pi + \alpha) = -\sin\alpha$", fontsize=12.5, fontweight='bold', pad=12)

    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    return save_path

def plot_limit_at_point(x0=2, L=4, save_path="limit_at_point.png"):
    """Vẽ minh họa giới hạn tại một điểm với điểm khuyết x0 và tiếp cận hai phía."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    x_left = np.linspace(x0 - 2, x0 - 0.02, 200)
    x_right = np.linspace(x0 + 0.02, x0 + 2, 200)
    y_left = x_left + 2
    y_right = x_right + 2

    ax.plot(x_left, y_left, color='#0284C7', lw=2.5, label=r'Đồ thị $y = f(x)$')
    ax.plot(x_right, y_right, color='#0284C7', lw=2.5)

    # Điểm khuyết (thủng)
    ax.scatter([x0], [L], s=120, facecolors='white', edgecolors='#DC2626', lw=2.5, zorder=6)
    ax.plot([x0, x0], [0, L], color='#94A3B8', ls=':', lw=1.5)
    ax.plot([0, x0], [L, L], color='#94A3B8', ls=':', lw=1.5)

    ax.axhline(0, color='#334155', lw=1.2)
    ax.axvline(0, color='#334155', lw=1.2)
    ax.text(x0, -0.3, rf'$x_0 = {x0}$', fontsize=11, fontweight='bold', ha='center', color='#DC2626')
    ax.text(-0.25, L, rf'$L = {L}$', fontsize=11, fontweight='bold', va='center', ha='right', color='#0284C7')

    plt.title(rf"BẢN CHẤT GIỚI HẠN TẠI MỘT ĐIỂM: $\lim_{{x \to {x0}}} f(x) = {L}$", fontsize=12, fontweight='bold', pad=12)
    ax.grid(True, ls='--', alpha=0.3)
    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    return save_path
