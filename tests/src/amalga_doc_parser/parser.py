    def _process_section_header(self, title_part: str, level: int, num        # Handle section hierarchy
        if level == 1:
            # Top-level section (level 1 headers)
            logger.info(f"Adding top-level section: {raw_name}")
            self.document.add_section(section)
            self.section_stack = [section]
        else:
            # For level 2+ headers, find the appropriate parent
            # Keep popping from section_stack until we find a section with lower level
            temp_stack = self.section_stack.copy()
            while temp_stack and temp_stack[-1].level >= level:
                temp_stack.pop()
                
            if temp_stack:
                # Found a parent
                parent = temp_stack[-1]
                logger.info(f"Adding subsection {raw_name} to parent {parent.raw_name}")
                parent.add_subsection(section)
                # Update the stack - all subsections at this level now belong to this parent
                self.section_stack = temp_stack + [section]
            else:
                # No parent found, add to root
                logger.warning(f"No parent found for {raw_name}, adding to root")
                self.document.add_section(section)
                self.section_stack = [section]
                logger.warning(f"No parent found for '{raw_name}', adding to root")
                self.document.add_section(section)
                self.section_stack = [section]
                
        self.current_section = section
