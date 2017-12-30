package de;


import javax.swing.*;

abstract class PaneTab extends JPanel {
    JFrame parentFrame;

    public PaneTab(JFrame parent) {
        parentFrame = parent;
    }
}