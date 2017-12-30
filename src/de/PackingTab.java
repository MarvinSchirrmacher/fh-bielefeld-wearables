package de;

import javax.swing.*;

public class PackingTab extends PaneTab {
    public PackingTab(JFrame parent) {
        super(parent);
        this.add(new JLabel("Pack your school bag"));

        JButton gpioTriggerButton = new JButton("Push me!");
        gpioTriggerButton.addActionListener(
                e -> JOptionPane.showMessageDialog(parentFrame, "I will set gpio 1 now!"));
        add(gpioTriggerButton);
    }
}
