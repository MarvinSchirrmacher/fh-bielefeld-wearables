package de;

import javax.swing.SwingUtilities;
import com.google.gson.Gson;
import com.sun.javaws.exceptions.InvalidArgumentException;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;

/**
 * Grafische Benutzerschnittstelle zur Bedienung und Konfiguration der intelligenten Schultasche.
 *
 * @author MarvinSchirrmacher
 * @since 30-12-2017
 *
 */
public class Program {
    /**
     * Programmeinstiegspunkt, der die eigentliche GUI-Anwendung startet.
     *
     * @param args Die optionalen Kommandozeilenparamter.
     */
    public static void main(String[] args) throws Exception {
        String configurationFilePath = args[0];
        File configurationFile = new File(args[0]);

        if (!configurationFile.isFile())
            throw new Exception(String.format("The file \"%s\" is no valid file", configurationFilePath));

        SwingUtilities.invokeLater(() -> {
            try {
                new SchoolBagManagement("Intelligente Schultasche", configurationFilePath);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
        });
    }
}
