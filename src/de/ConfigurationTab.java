package de;

import javax.swing.*;

class ConfigurationTab extends PaneTab {
    ConfigurationTab(JFrame parent, SchoolBagSettings settings) {
        super(parent);
        add(new JLabel("Manage your data"));
        add(new JTextField(settings.getHeight().toString()));
        add(new JTextField(settings.getWeight().toString()));
        add(new JTextField(settings.getBirthday().toString()));
    }
}

