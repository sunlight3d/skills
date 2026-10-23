#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module tự động vẽ đồ thị, hình minh họa hình học, trục số, miền nghiệm
theo phong cách sư phạm chuẩn MathPlus Academy (sắc nét, trang nhã, 220+ DPI).
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

# Thiết lập font và style chung
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#475569'
plt.rcParams['axes.linewidth'] = 0.8

def setup_cartesian_axis(ax, xlim, ylim, xlabel='x', ylabel='y'):
    """Tạo hệ trục tọa độ vuông góc Oxy với mũi tên và gốc tọa độ O."""
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    
    # Mũi tên trục Ox và Oy
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=5)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=5)
    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel(xlabel, loc='right', fontsize=11, fontweight='bold', color='#1E293B', labelpad=-12)
    ax.set_ylabel(ylabel, loc='top', fontsize=11, fontweight='bold', color='#1E293B', labelpad=-12)
    ax.text(-0.35, -0.35, 'O', fontsize=10, fontweight='bold', color='#1E293B')
    ax.grid(True, linestyle=':', alpha=0.5, color='#94A3B8')

def plot_number_line_intervals(intervals, output_path, x_range=(-5, 7), figsize=(7.2, 3.6), dpi=220):
    """
    Biểu diễn các tập hợp trên trục số.
    
    Args:
        intervals: List of tuples (title, a, b, left_bracket, right_bracket)
                   ví dụ: [("Tập A = [-3; 4)", -3, 4, '[', ')'), ...]
        output_path: Đường dẫn lưu file ảnh png
    """
    n = len(intervals)
    fig, axes = plt.subplots(n, 1, figsize=figsize, dpi=dpi)
    if n == 1:
        axes = [axes]
        
    fig.subplots_adjust(hspace=0.6, left=0.18, right=0.92, top=0.92, bottom=0.1)
    min_x, max_x = x_range
    x_ticks = list(range(int(min_x), int(max_x) + 1))
    
    for i, ax in enumerate(axes):
        ax.set_xlim(min_x - 0.5, max_x + 0.5)
        ax.set_ylim(-0.5, 0.5)
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.spines['bottom'].set_position('zero')
        ax.spines['bottom'].set_color('#334155')
        ax.spines['bottom'].set_linewidth(1.2)
        
        ax.plot(max_x + 0.5, 0, ">k", clip_on=False, markersize=6)
        
        for x in x_ticks:
            ax.plot([x, x], [-0.08, 0.08], color='#64748B', lw=0.8)
            ax.text(x, -0.35, str(x), ha='center', va='center', fontsize=8, color='#334155')
            
        title, a, b, left_br, right_br = intervals[i]
        
        # Gạch sọc phần bên ngoài khoảng/đoạn
        if a is not None:
            for x in np.arange(min_x - 0.5, a, 0.25):
                ax.plot([x, x + 0.15], [-0.15, 0.15], color='#94A3B8', lw=1.0)
        if b is not None:
            for x in np.arange(b, max_x + 0.5, 0.25):
                ax.plot([x, x + 0.15], [-0.15, 0.15], color='#94A3B8', lw=1.0)
                
        # Đoạn lấy nghiệm
        draw_a = min_x - 0.5 if a is None else a
        draw_b = max_x + 0.5 if b is None else b
        ax.plot([draw_a, draw_b], [0, 0], color='#0F4C81', lw=3.0)
        
        if a is not None:
            ax.text(a, 0, left_br, ha='center', va='center', fontsize=14, fontweight='bold', color='#DC2626')
        if b is not None:
            ax.text(b, 0, right_br, ha='center', va='center', fontsize=14, fontweight='bold', color='#DC2626')
            
        ax.set_yticks([])
        ax.set_xticks([])
        ax.text(min_x - 1.0, 0, title, ha='right', va='center', fontsize=9.5, fontweight='bold', color='#0F4C81')
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path

def plot_linear_inequality(a, b, c, op, output_path, xlim=(-2, 5), ylim=(-2, 6), title=None, dpi=220):
    """
    Biểu diễn miền nghiệm của bất phương trình bậc nhất 2 ẩn ax + by (op) c.
    op in ['<=', '>=', '<', '>']
    """
    fig, ax = plt.subplots(figsize=(5.2, 4.2), dpi=dpi)
    setup_cartesian_axis(ax, xlim, ylim)
    
    x = np.linspace(xlim[0], xlim[1], 300)
    if b != 0:
        y = (c - a*x) / b
        ax.plot(x, y, color='#0F4C81', lw=2.2, label=f'd: {a}x + {b}y = {c}')
        # Tô màu miền nghiệm
        if op in ['<=', '<']:
            if b > 0:
                ax.fill_between(x, ylim[0], y, where=(y >= ylim[0]), color='#93C5FD', alpha=0.35, label='Miền nghiệm')
            else:
                ax.fill_between(x, y, ylim[1], where=(y <= ylim[1]), color='#93C5FD', alpha=0.35, label='Miền nghiệm')
        else: # >=, >
            if b > 0:
                ax.fill_between(x, y, ylim[1], where=(y <= ylim[1]), color='#93C5FD', alpha=0.35, label='Miền nghiệm')
            else:
                ax.fill_between(x, ylim[0], y, where=(y >= ylim[0]), color='#93C5FD', alpha=0.35, label='Miền nghiệm')
                
    ax.scatter([0], [0], color='#16A34A', s=35, zorder=5)
    ax.text(-0.5, 0.4, 'O(0;0)', fontsize=9, color='#16A34A', fontweight='bold')
    
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.9)
    if title:
        ax.set_title(title, fontsize=10.5, fontweight='bold', color='#0F4C81', pad=10)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path

def plot_linear_system_polygon(lines_data, vertices, output_path, xlim=(-1, 7), ylim=(-1, 6), title=None, dpi=220):
    """
    Biểu diễn miền nghiệm đa giác của hệ bất phương trình bậc nhất hai ẩn.
    """
    fig, ax = plt.subplots(figsize=(5.4, 4.4), dpi=dpi)
    setup_cartesian_axis(ax, xlim, ylim)
    
    x = np.linspace(xlim[0], xlim[1], 300)
    for lbl, y_func, color, ls in lines_data:
        ax.plot(x, y_func(x), color=color, lw=1.8, linestyle=ls, label=lbl)
        
    pts = np.array([[vx, vy] for vx, vy, _ in vertices])
    poly = Polygon(pts, closed=True, facecolor='#60A5FA', alpha=0.45, edgecolor='#0F4C81', lw=2.2, label='Miền nghiệm đa giác')
    ax.add_patch(poly)
    
    for vx, vy, vlabel in vertices:
        ax.scatter([vx], [vy], color='#DC2626', s=45, zorder=6)
        ax.text(vx + 0.15, vy + 0.15, vlabel, fontsize=9.5, fontweight='bold', color='#DC2626')
        
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.9)
    if title:
        ax.set_title(title, fontsize=10.5, fontweight='bold', color='#0F4C81', pad=10)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path

def plot_quadratic_parabola(a, b, c, output_path, xlim=(-2, 6), ylim=(-10, 4), title=None, key_pts=None, dpi=220):
    """
    Vẽ đồ thị parabol y = ax^2 + bx + c.
    """
    fig, ax = plt.subplots(figsize=(5.2, 4.4), dpi=dpi)
    setup_cartesian_axis(ax, xlim, ylim)
    
    x = np.linspace(xlim[0] + 0.5, xlim[1] - 0.5, 300)
    y = a*x**2 + b*x + c
    ax.plot(x, y, color='#0F4C81', lw=2.4, label=f'$y = {a}x^2 {"+" if b>=0 else ""}{b}x {"+" if c>=0 else ""}{c}$')
    
    vx = -b / (2*a)
    vy = a*vx**2 + b*vx + c
    ax.axvline(x=vx, color='#DC2626', linestyle=':', lw=1.6, label=f'Trục đối xứng x = {vx:g}')
    
    if key_pts:
        for px, py, plabel, (off_x, off_y) in key_pts:
            ax.scatter([px], [py], color='#DC2626', s=38, zorder=5)
            ax.text(px + off_x, py + off_y, plabel, fontsize=9, fontweight='bold', color='#1E293B')
            
    ax.plot([vx, vx], [0, vy], 'k--', lw=0.9, alpha=0.6)
    ax.plot([0, vx], [vy, vy], 'k--', lw=0.9, alpha=0.6)
    
    ax.legend(loc='best', fontsize=8.5, framealpha=0.9)
    if title:
        ax.set_title(title, fontsize=10.5, fontweight='bold', color='#0F4C81', pad=10)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    return output_path
